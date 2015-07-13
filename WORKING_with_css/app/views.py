#!/usr/bin/env python
# from datetime import datetime
from dateutil import tz
from geopy.distance import vincenty
from flask import render_template
from app import app
from flask import abort, redirect, url_for, flash, Flask, request
from twython import Twython, TwythonStreamer
import json, datetime, requests, humanize, string, psycopg2, pytz

from QueryUsers import *

# For connecting to Twitter Stream using OAuth 1
APP_KEY = 'GLIC9scXNOCQPMvW2Z3vDR0gP'
APP_SECRET = 'r4pxcSzlCyaHiTR5QFSpN20nLn24XXV06YL8gtxGUzc4wXhgLA'
ACCESS_TOKEN = '2875905140-02P20c7dHFDgb9yIE2jEqdlidS9xOGkdVq4nrGB'
ACCESS_TOKEN_SECRET = '42azhlc7p4Hi949NvPth3FmdJ8bZafzGqLIrAHKTXDOSi'

APP_KEY = 'UmLjRKeW4Gc9RlLUBqoNfpmyG'
APP_SECRET = 'qFCKEMZbLD7NO4ki2ksbibQ01SV88ECJQLZn3TQmQXiJkvN877'
ACCESS_TOKEN = '3307752328-R52HmpgczQt5tl8hYohaXZ9j0moNMOfAemNEdd1'
ACCESS_TOKEN_SECRET = 'eJNVo321y9Ancj08oJOo9Ii4KFHJIJgbyFSgaRuMGHb3x'

recentTweeters = []
class NEW_QUESTION: 
    # default values 
    city = "Pittsburgh"
    venue = "Schenley Plaza"
    usernames = ["jinnyhyunjikim"]
    question = "How many college students do you see at Schenley Plaza right now?"
    topic = "park usage"
    q_id = 0 # question_id in tweetdb
    
nq = NEW_QUESTION()
twitter = Twython(APP_KEY, APP_SECRET,
                  ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
twitter.verify_credentials()

def sendTweet(user_to_ask, question_text):
    question_statement = "@" + user_to_ask + " " + question_text # e.g. '@jinny6235 Good afternoon!'
    print "SEDING TWEET!" + question_statement
    twitter.update_status(status = question_statement) # send tweet
    #sending duplicate tweet to same user as last one returns error 

    print " TWEET sent: " + user_to_ask + "!"
    print "updated database: QUESTION_TWEET"

# Insert data to psql tweet db
def updateDatabase(tablename, *data):
    columns_question = '(question_id, topic, question_text, expected_response_type, venue, city, created_at, expires_at)'
    columns_response = '(response_id, response_raw, response_parsed, in_reply_to, user_id, created_at)'
    columns_question_tweet = '(tweet_id, question_id, user_id)'
    columns_question_user = '(user_id)'

    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()

    data = list(data)
    data = tuple(data) 
    values = str(data)

    if tablename == 'question_response':
        columns = str(columns_response)
    elif tablename == 'question':
        columns = str(columns_question)  
    elif tablename == 'question_user':
        columns = str(columns_question_user)
    elif tablename == 'question_tweet':
        columns = str(columns_question_tweet)
    else:
        print "Error: No such table to update!"

    statement = "INSERT INTO " + tablename + " " + columns + " VALUES " + values + ";"
    cur.execute(statement)
    conn.commit()

# Get next unique id for new row in question and question_user
# question_tweet and question_user use id from twitter
def getNextRowID(tablename):
    # Connect to response table in the database
    conn = psycopg2.connect("dbname=tweet user=jinnyhyunjikim")
    cur = conn.cursor()

    # Query the response_id of the last element
    if tablename == 'question':
        print "querying for question"
        query = "SELECT max(question_id) FROM question;"
    elif tablename == 'question_user':
        query = "SELECT max(user_id) FROM question_user;"
    else:
        print "Error: No such table in psql tweet database."
        return

    cur.execute(query)
    result = cur.fetchone()

    print 'here '
    print result
    largest_id = result[0]
    print largest_id
    if largest_id == None: # table empty
        return 0
    return largest_id + 1

def getCorrespondingTweetIds(question_id):
    # returns a list of tweet_id's sending out the question
    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()
    query = "SELECT tweet_id FROM question_tweet WHERE question_id = %s;" % (question_id)
    cur.execute(query)
    tweet_ids = list_of_corresponding_tweets = cur.fetchall() # returns a 2d list
    tweet_ids = [first_element for first_element, in tweet_ids]
    return tweet_ids

def getRepliesToATweet(tweet_id):
    # returns a list of replies made to a given tweet, identified by its tweet id
    # each reply is made into a dictionary
    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()
    print "getting replies"
    # statement = """SELECT response_id, response_raw, response_parsed, question_response.user_id, question_response.created_at FROM question_response INNER JOIN question_tweet ON (question_tweet.tweet_id = question_response.in_reply_to) WHERE (question_tweet.tweet_id = %s) ; """ % (tweet_id)
    statement = """SELECT response_id, response_raw, response_parsed, question_response.user_id, question_id, created_at FROM question_response INNER JOIN question_tweet ON (question_tweet.tweet_id = question_response.in_reply_to) WHERE (question_tweet.tweet_id = %s) ; """ % (tweet_id)
    print 'statement : ' + statement
    cur.execute(statement)

    columns = ('response_id', 'response_raw', 'response_parsed', 'user_id', 'question_id', 'created_at' )
    replies = cur.fetchall()
    results = []
    for reply in replies:
        results.append(dict(zip (columns, reply)))
    conn.commit()
    cur.close()
    conn.close()
    print "Returning this as replies to a tweet "
    print results
    return results

def getResponsesForQuestion(question_id):
    # Given question_id, get all tweet responses to that question.
    # 1. Get all tweet_id's sending out that question.
    # 2. Get all tweet_responses replying to those tweets.
    all_replies = []
    tweet_ids = getCorrespondingTweetIds(question_id)
    print "getting corresponding tweet ids " 
    print tweet_ids

    for one_tweet in tweet_ids:
        replies = getRepliesToATweet(one_tweet)
        all_replies += replies
    
    return all_replies

def getDistance(coordinates1, coordinates2):
# Takes in two tuples of lat/long points and calculates 
# Returns the distance in miles.
    distance = vincenty(coordinates1, coordinates2).miles
    return distance

# def removeDecimalPointInSeconds(timestamp_string):
# # takes in '2015-07-07 15:08:03.745033'
# # returns 2015-07-06 15:15:13.391368+00:00

#     seconds_decimal_point = timestamp_string.index(".")
#     timestamp_string = timestamp_string[:seconds_decimal_point]

# Convert UTC timestamp created by db to local (EST) time
def convertUTCtoLocalTime(timestamp_string):
    
    # remove decimal point in seconds
    seconds_decimal_point = timestamp_string.index(".")
    timestamp_string = timestamp_string[:seconds_decimal_point]

    # METHOD 1: Hardcode zones:
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York') # for EST

    # METHOD 2: Auto-detect zones:
    # from_zone = tz.tzutc()
    # to_zone = tz.tzlocal()

    # utc = datetime.utcnow()
    utc = datetime.datetime.strptime(timestamp_string, '%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    eastern = utc.astimezone(to_zone)
    return eastern

# Start of web app code
@app.route('/')
@app.route('/index')
def index():
    print "loading index page"
    user = {'nickname': 'City of Pittsburgh'}
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    print 'rending'
    return render_template("index.html",
                           title='Home',
                           user=user,
                           open_questions=posts,
                           closed_questions=posts)

@app.route('/question')
def question():
    user = {'nickname': 'Miguel'}
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("question.html",
                           title='Question page',
                           user=user,
                           posts=posts)

def getRelativeTime(timestamp):
# Takes in a timestamp with timezone and
# returns humanized form of time difference btwn now and then
    timestamp = timestamp.replace(tzinfo=None) # strip timezone 
    now =  datetime.datetime.now()
    relativeTime = humanize.naturaltime( now - timestamp )
    return relativeTime

@app.route('/responses')
def responses():
    user = {'nickname': 'Miguel'}
    responses = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    def getQuestions(open_or_closed):
        # Get questions. Type specifies 'open' or 'closed' (expired or not)
        # Returns a list of questions, each in dict format
        conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
        cur = conn.cursor()
        print "Getting questions" + open_or_closed
        if open_or_closed == "open": # get questions that have not yet expired
            statement = """SELECT question_id, question_text, venue, city, created_at FROM question WHERE expires_at > now() ORDER BY created_at DESC ; """
        else:
            statement = """SELECT question_id, question_text, venue, city, created_at FROM question WHERE expires_at < now() ORDER BY created_at DESC ; """
        print statement
        cur.execute(statement)
        questions = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        # Build dictionary for each question
        list_of_questions = [] # will insert each dictionary here
        columns = ('question_id', 'question_text', 'venue', 'city', 'created_at') ###
        for question in questions:
            list_of_questions.append(dict(zip (columns, question)))
        # Adjust to EST time (psql tweet stores UTC time)
        for question in list_of_questions:
            created_at = question['created_at']
            # utc_time = str(utc_time)
            # est_time = convertUTCtoLocalTime(utc_time)
            # question['created_at'] = est_time
            question['time_since'] = getRelativeTime(created_at)

        # Add replies to those tweets
        for question in list_of_questions:
            question_id = question['question_id']
            replies = getResponsesForQuestion(question_id)
            question['responses'] = replies # a list of dict of replies
        
        for question in list_of_questions:
        	print question['question_text']

        return list_of_questions

#    def getOpenQuestions():
#    # Get questions that have not yet expired
#    # Returns a list of questions, each in dict format
#        conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
#        cur = conn.cursor()
#        statement = """SELECT question_id, question_text, venue, city, created_at FROM question WHERE expires_at > now() ORDER BY created_at DESC ; """
#        cur.execute(statement)
#        open_questions = cur.fetchall()
#        conn.commit()
#        cur.close()
#        conn.close()
#
#        # Build dictionary for each question
#        list_of_open_questions = [] # will insert each dictionary here
#        columns = ('question_id', 'question_text', 'venue', , 'city', 'created_at') ###
#        for question in open_questions:
#            list_of_open_questions.append(dict(zip (columns, question)))
#
#        # Adjust to EST time (psql tweet stores UTC time)
#        for question in list_of_open_questions:
#            utc_time = question['created_at']
#            utc_time = str(utc_time)
#            est_time = convertUTCtoLocalTime(utc_time)
#            question['created_at'] = est_time
#
#        # Add replies to those tweets
#        for question in list_of_open_questions:
#            question_id = question['question_id']
#            replies = getRepliesForQuestion(question_id)
#            question['responses'] = replies # a list of dict of replies
#
#        return list_of_open_questions

#    def getClosedQuestions():
#        conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
#        cur = conn.cursor()
#        # statement = "SELECT venue FROM question WHERE expires_at > now(); " 
#        statement = "SELECT venue, question_text, city, question_id, created_at FROM question WHERE expires_at < now() ; "  
#        cur.execute(statement)
#        open_questions = cur.fetchall()
#        conn.commit()
#        cur.close()
#        conn.close()
#
#        # Create dictionary with the info
#        list_of_open_questions = [] # will create dictionary in here
#        columns = ('venue', 'text', 'city', 'question_id', 'created_at')
#        for question in open_questions:
#            list_of_open_questions.append(dict(zip (columns, question)))
#
#        # Adjust to EST time (psql tweet stores UTC time)
#        for question in list_of_open_questions:
#            utc_time = question['created_at']
#            utc_time = str(utc_time)
#            est_time = convertUTCtoLocalTime(utc_time)
#            question['created_at'] = est_time
#
#        # Add responses to those tweets
#        for question in list_of_open_questions:
#            question_id = question['question_id']
#            responses = getResponsesForQuestion(question_id)
#            question['responses'] = responses # gives a list of dict of responses
#
#        # each response now has variables 'venue', 'text', 'city', 'question_id', 'created_at', 'responses'
#        return list_of_open_questions 

    # questions = str(getOpenQuestions()
#    open_questions = getOpenQuestions()
#    closed_questions = getClosedQuestions()
    open_questions = getQuestions("open")
    print '======got open questions===='
    closed_questions = getQuestions("closed")
    print 'gotclosed questions'
    return render_template("responses.html",
                           title='Responses page',
                           user=user,
                           questions=open_questions,
                           closed_questions=closed_questions)

@app.route('/recent_tweeters')
def recent_tweeters():
    print 'here, in recent_tweets html page'
    users = { 'username' : 'jinnyhyunjikim' }
    # recent_tweeters = recentTweeters
    # print recent_tweeters
    # if request.method == 'POST':
    #     venue_name = str(request.form['venue_name'])
    #     print 'HERE!!!! VENUE NAME'
    #     print venue_name
    #     recent_tweeters = find_the_tweeters(venue_name)
    #     render_template('recent-tweeters.html', users=users)
    # else:
    #     print 'here'
    #     return render_template('recent-tweeters.html')
    users = nq.usernames
    print 'USERS TO DISPLAY:'
    print users
    # return render_template('query_result.html', users=users)
    return render_template(url_for('query_result'), users=users)

def find_the_tweeters(venue_name= None):
    print 'finding the tweeters...'
    print 'venue name: ' + venue_name
    recentTweeters = QueryTwitterUsers.query(last_tweet_venue_name = venue_name)
    return recentTweeters

@app.route('/show_answerers')
def show_answerers():
    # Get X number of people who tweeted at the area / venue within the past X minutes
    def getUsersToAsk(city = "tweet_pgh", venue = "Pittsburgh",
                                                     how_many = 2, type = "at"):
        return ["jinnyhyunjikim"] # testing

        city = "tweet_pgh" # or 'tweet_ny', 'tweet_sf', 'tweet_boston'
        search_limit = how_many
        venue = venue
        
        # query = """SELECT DISTINCT user_screen_name FROM %s 
        #             WHERE created_at >= (now() - interval '5 minutes') 
        #             AND place-> 'full_name' = '%s' limit %d""" % (city, _venue_, _search_limit_)
        query = """SELECT DISTINCT user_screen_name FROM %s 
                    WHERE created_at >= (now() - interval '5 minutes') 
                    limit %d;""" % ( city, search_limit )
        conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return result

    def getUsersToAsk_method2(city = 'tweet_pgh', venue = 'Schenley Plaza',
                                                how_many = 5, type = 'park', nearby ="near"):
    # takes in a venue name and type, e.g. "Schenley Park", "park" or 
    # "Forbes+Craig","cross-section"

    # nearby = "near" - within .5 mi or "at" - within the bounding box 
    # returns a list of how_many users who tweeted NEAR that venue within
    # last X minutes
        # Get the coordinates of the venue
        return ['jinnyhyunjikim']
        def getVenueID(venue_name):

        	return
        def getCoordinatesOfVenue(venue_name):

	        CLIENT_ID ='0015X0KQ1MLXKW0RTDOCOKUMACBCKE30ZY2IFYPCQDYTZ3EC'
	        CLIENT_SECRET = 'UKJRW30YZAXC5DUO5KOZFPM4XWD3O3YSK0ANCZKB3TYCMCA5'

	        url = 'https://api.foursquare.com/v2/venues/search?match=true&limit=1'
	        city = 'near=%s' % ( 'pittsburgh,pa' )
	        venue_name = 'query=%s' % ( venue ) 	        # print venue_name
	        client_id = 'client_id=' + CLIENT_ID
	        client_secret = 'client_secret='+ CLIENT_SECRET
	        url_complete = url + '&' + city + '&' + venue_name + '&' + client_id + '&' + client_secret+'&v=20150707'
	        # client_secret = '&client_secret='+ CLIENT_SECRET&v=YYYYMMDD
	        # oauth_token = '%oauth_token=' + 'SIVKZ0OBXJOO5DO3IJUZ2YDHGEBO4RCY3O3DVJTUE0IN1STQ&v=20150707' 

	        print url_complete
	        # url = 'https://api.foursquare.com/v2/venues/search?near=New+Delhi&intent=browse&radius=10000&limit=10&query=pizza+hut' + client_id + '&' + client_secret + '&v=20150707'
	        
	        response = requests.get(url_complete)
	        response = response.json()

	        print 'queried!'

	        # check the query is valid
	        valid = response['meta']['code']
	        if valid == 200:
	            first_venue = response['response']['venues'][0]
	            first_venue_id = first_venue['id']
	            first_venue_location = first_venue['location']
	            keys = first_venue_location.keys()
	            print 'keys'
	            print keys
	            print 'VNUE ID :  '
	            print first_venue_id
	            print 'VNUE LOCATIONN:  '
	            latitude = first_venue_location['lat']
	            print 'here'
	            print latitude
	            longitude = first_venue_location['lng']
	            # print type(latitude)
	            print 'after long'
	            print longitude
	            print 'after long'
	            return (latitude, longitude)
	        else: 
	            print 'No location found. Please check the venue name'
	            return -1

        # Get users whose location within X minutes was within Y miles 
        # of the venue's coordinates
        coordinates_venue = getCoordinatesOfVenue(venue)
        if coordinates_venue == -1:
        	return
        else:
        	users_near = getNearUsers(coordinates_venue)

        def getUsersNearby(coordinate_points):
        # Takes in a tuple of latitude and longitude points and 
        # Returns a list of users from question_user db who has tweeted 
        # within X mi of the given points in the last 5 minutes

        	# Get users who tweeted within the last 5 minutes
            search_limit = 5
            query = """SELECT user_id FROM question_user
                        WHERE last_tweet_timestamp >= (now() - interval '5 minutes') 
                        limit %d;""" % ( search_limit )
            conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
            cur = conn.cursor()
            cur.execute(query)
            recent_tweeters = cur.fetchall()  # -> get list of userids
            conn.commit()
            cur.close()
            conn.close()
            

        	# Filter users who were within X mi of the given points
            users_nearby = []
            proximity = 0.05 # miles
            # for recent_tweeter in recent_tweeters:
                # get last coordinates of the tweeter 
                # coordinates_tweeter = getMostRecentLocation

                # calculate distance
                # distance = getDistance(coordinates_venue, coordinates_tweeter)
                # if distance < proximity:
                    # users_nearby.append(recent_tweeter)
            return users_nearby


    # nq.usernames = getUsersToAsk()
    nq.usernames = getUsersToAsk_method2()
    print 'got users!'
    usernames_to_display = []
    one_username = dict()
    print 'here'
    for username in nq.usernames:
            one_username['username'] = username
            usernames_to_display.append(one_username)
    print "USERNAMES as a list :" 
    print usernames_to_display
    for username in usernames_to_display:
        print username['username']

    print type(usernames_to_display)
    count = len(usernames_to_display)
    print 'VENUE! ' + nq.venue
    return render_template('show_answerers.html', venue=nq.venue, count=count, 
                usernames=usernames_to_display) 

# Store city, venue, question, and topic values given by the user
@app.route('/answerers', methods=['POST'])
def answerers():
    error = None
    nq.city = str(request.form['city'])
    nq.venue = str(request.form['venue'])
    nq.question = str(request.form['question'])
    nq.topic = str(request.form['topic'])
    nq.q_id =  getNextRowID("question") # incremental question_id in db
    return redirect(url_for('show_answerers'))
#    return render_template(url_for('show_answerers')) # does not work
#    return render_template(url_for('show_answerers.html')) # does not work
#    return redirect(url_for('show_answerers'))

@app.route('/get_recent_tweeters', methods=['POST'])
def get_recent_tweeters():
    print request.form['city']
    print request.form['venue-name']
    venue_name = str(request.form['venue-name'])

    print 'HERE!!!! VENUE NAME'
    print venue_name
    nq.usernames = find_the_tweeters(venue_name)
    return redirect(url_for('recent_tweeters'))

# Send questions to individual user
@app.route('/send_question', methods=['POST'])
def send_question():
    q_id = nq.q_id
    city = nq.city 
    venue = nq.venue
    question = nq.question
    topic = nq.topic
    tor = type_of_response = "numeric" # only numberic supported now with response db
    
    expire_after = 30 # minutes
    datetime_now = datetime.datetime.now()
    datetime_expire = datetime_now + datetime.timedelta(minutes=expire_after)
    datetime_now = str(datetime_now) # e.g. '2015-07-04 17:23:42.636711'
    datetime_expire = str(datetime_expire)
    datetime_expire = '2015-07-10 17:23:42.636711' # extended for testing

    print "updating database: QUESTION ... "
    # Insert this asking instance to question db
    updateDatabase("question", q_id, topic, question,
                            tor, venue, city, datetime_now, datetime_expire)
    print "done updating database: QUESTION "

    # Send tweet to individual username
    # Each tweet instance gets collected and stored from twitter stream,
    # not when being sent
    usernames = nq.usernames
    for username in usernames:
    	x= 2
        sendTweet(username, question)
    return redirect(url_for('question_sent')) ### return to question sent! ?


@app.route('/question_sent')
def question_sent():
    print 'entires '
    entries = [
        {'username': 'one'},
        {'username': 'two'}
    ]
    question = nq.question
    users = nq.usernames
    print question 
    print users
    # time = current_time
    return render_template('question_sent.html', question=question, users=users)



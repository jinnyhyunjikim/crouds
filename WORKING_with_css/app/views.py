#!/usr/bin/env python

from dateutil import tz
from geopy.distance import vincenty
from flask import render_template
from app import app
from flask import abort, redirect, url_for, flash, Flask, request
from twython import Twython, TwythonStreamer
import json, requests, humanize, string, psycopg2, pytz, copy
from datetime import datetime, timedelta
from FindUsers import *
from GetQuestions import *
from AddQuestion import * 
from GetResponses import *

# To connect to Twitter Stream using OAuth 1
APP_KEY = 'GLIC9scXNOCQPMvW2Z3vDR0gP'
APP_SECRET = 'r4pxcSzlCyaHiTR5QFSpN20nLn24XXV06YL8gtxGUzc4wXhgLA'
ACCESS_TOKEN = '2875905140-02P20c7dHFDgb9yIE2jEqdlidS9xOGkdVq4nrGB'
ACCESS_TOKEN_SECRET = '42azhlc7p4Hi949NvPth3FmdJ8bZafzGqLIrAHKTXDOSi'

APP_KEY = 'UmLjRKeW4Gc9RlLUBqoNfpmyG'
APP_SECRET = 'qFCKEMZbLD7NO4ki2ksbibQ01SV88ECJQLZn3TQmQXiJkvN877'
ACCESS_TOKEN = '3307752328-R52HmpgczQt5tl8hYohaXZ9j0moNMOfAemNEdd1'
ACCESS_TOKEN_SECRET = 'eJNVo321y9Ancj08oJOo9Ii4KFHJIJgbyFSgaRuMGHb3x'

# twitter.verify_credentials()

class UserSearch:

    def __init__(self):
        self.minutes = None
        self.home = None
        self.last_tweet_venue_name  = None
        self.last_tweet_venue_id  = None
        self.last_tweet_streets = None
        self.search_result = []

    def reset(self):
        self.minutes = None
        self.home = None
        self.last_tweet_venue_name  = None
        self.last_tweet_venue_id  = None
        self.last_tweet_streets = None
        self.search_result = []

class NewQuestion: ### 

    def __init__(self):
        self.minutes = None
        self.home = None
        self.location = None
        self.location_type = None
        self.open_at = None
        self.close_at = None 
        # self.location = {'location_type': None, 'venue-name': None, 'venue-id': None, 'streets': [None, None]}
        # self.last_tweet_venue_name  = None
        # self.last_tweet_venue_id  = None
        # self.last_tweet_streets = None

    def reset(self):
        self.minutes = None
        self.home = None
        self.location = None
        self.location_type = None
        self.open_at = None
        self.close_at = None 

twitter = Twython(APP_KEY, APP_SECRET,
                  ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
search = UserSearch()
new_question = NewQuestion()


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
    distance = vincenty(coordinates1, coordinates2).miles
    return distance

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/view_questions')
def view_questions():
    open_questions = GetQuestions.get_open_questions()
    return render_template('view_questions.html', open_questions= open_questions)

@app.route('/new_question')
def new_question():
    return render_template('new_question.html')

@app.route('/responses')
@app.route('/responses_parsed')
def responses():
    responses = GetResponses.get_responses()
    return render_template("responses_parsed.html", responses= responses)

@app.route('/show_recent_tweeters' )
def show_recent_tweeters():
    result = search.search_result
    search.reset()
    return render_template('show_recent_tweeters.html',users=result) 

@app.route('/enqueue_question', methods=['POST'])  ###
def enqueue_question():
    new_question = NewQuestion()
    print 'enqueueing '
    new_question.subject = str(request.form['subject'])
    new_question.question = str(request.form['question'])
    print 'here'
    new_question.open_at = open_at = str(request.form['open_at']) # '2000-01-01T05:00'
    new_question.close_at = close_at = str(request.form['close_at'])

    print 'hrd'
    if request.form['location'] == 'venue-name':
        new_question.location = 'venue name'
        # new_question.location['location_type'] = 'venue name' 
        # new_question.location['venue_name'] = str(request.form['venue-name'])
        new_question.location = str(request.form['venue-name'])
    elif request.form['location'] == 'venue-id': 
        new_question.location = 'venue id'
        # new_question.location['location_type'] = 'venue id' 
        # new_question.location['venue_id'] = str(request.form['venue-id'])
        new_question.location= str(request.form['venue-id'])

    elif request.form['location'] == 'streets': 
        new_question.location = 'streets'
        # new_question.location['location_type'] = 'streets' 
        street_1, street_2 = str(request.form['venue-street-1']), str(request.form['venue-street-2'])
        # new_question.location['streets'] = [street_1, street_2]
        new_question.location = street_1 + '&' + street_2
    print new_question.location

    open_at = datetime.strptime(open_at, '%Y-%m-%dT%H:%M') # covert to datetime
    close_at = datetime.strptime(close_at, '%Y-%m-%dT%H:%M')
    delta = timedelta(minutes=5)
    send_times = new_question.send_times = perdelta(open_at, close_at, delta) # returns list of datetimes
    AddQuestion.add(new_question) # add question to db
    return redirect(url_for('view_questions'))

@app.route('/find_tweeters', methods=['POST']) 
def find_tweeters():
    search.minutes = request.form['minutes']
    search.home = request.form['home-neighborhood']
    print search.home
    if search.home == 'Any': search.home = None
    if request.form['location'] == 'venue-name': search.last_tweet_venue_name = request.form['venue-name']
    if request.form['location'] == 'venue-id': search.last_tweet_venue_id = request.form['venue-id']
    if request.form['location'] == 'streets': search.last_tweet_streets = (request.form['venue-street-1'], request.form['venue-street-2'])

    search.search_result = FindUsers.search(  
                minutes_since = search.minutes,
                home = search.home,
                venue_name = search.last_tweet_venue_name,
                venue_id = search.last_tweet_venue_id,
                streets = search.last_tweet_streets)
    return redirect(url_for('show_recent_tweeters'))





# Helper Fn's




def perdelta(start, end, delta):
# start, end = date/time/datetime
# delta = timedelta
    print 'in perdelta'
    times = []
    curr = start
    while curr < end:
        print str(curr)
        times.append(curr)

        curr += delta
    return times


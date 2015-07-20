#!/usr/bin/python

import string, psycopg2, requests, json, csv, time
from datetime import datetime, date
from geopy.distance import vincenty

class FindUsers():

    @staticmethod
    def search(  
                within_x_minutes = None,
                home_neighborhood = None,
                last_tweet_neighborhood = None,
                last_tweet_venue_category = None,
                last_tweet_venue_name = None,
                last_tweet_venue_id = None,
                last_tweet_streets = None
            ):

        # print 'Making a request for users within ' + str(within_x_minutes) + ' minutes...' 
        print 'Making a request for users within last 30 days...' 
        query_start_time = time.time()

        searched_for = None
        dict_to_return = {}
        dict_to_return['criteria'] = []

        # Get all recent tweeters.
        all_recent_tweets = get_all_recent_tweets(minutes= within_x_minutes)

        dict_to_return['total_recent_tweet_count'] = len(all_recent_tweets)

        # Filter by last tweet location.
        matching_tweets = all_recent_tweets
        if  last_tweet_venue_name != None: 
            dict_to_return['criteria'].append('venue-name') 
            matching_tweets = filter_by_venue(tweets= matching_tweets, 
                                        venue_name= last_tweet_venue_name)
            print 'filtered after venue - ' + str(len(matching_tweets))
        elif last_tweet_venue_id != None:
            dict_to_return['criteria'].append('venue-id') 
            matching_tweets = filter_by_venue(tweets= matching_tweets, 
                                        venue_id= last_tweet_venue_id)
            print 'filtered after venue - ' + str(len(matching_tweets))
        elif last_tweet_streets != None:
            dict_to_return['criteria'].append('streets') 
            matching_tweets = filter_by_streets(tweets= matching_tweets,
                                              streets= last_tweet_streets)
            print 'filtered after streets - ' + str(len(matching_tweets))
        matching_tweets = filter_by_home(tweets= matching_tweets,  
                                    neighborhood = home_neighborhood)
        if home_neighborhood != None:
            dict_to_return['criteria'].append('home-neighborhood') 
            print 'filtered after home - ' + str(len(matching_tweets))


        # Filter non-volunteers. 
        matching_tweets = remove_non_volunteers(matching_tweets)
        dict_to_return['search_result'] = matching_tweets 
        elapsed_time = time.time() - query_start_time
        dict_to_return['query_duration'] = str(elapsed_time)
        return dict_to_return

def get_all_recent_tweets(minutes):

    max_search_limit = None
    if max_search_limit == None: max_search_limit = 300

    # Limit search to first x found CORRECT ONE 

    query_statement = """SELECT user_screen_name, text, ST_AsGeoJSON(coordinates)
                        from tweet_pgh 
                        WHERE created_at >= (now() - interval '%s minutes') 
                        limit %s; """ % (minutes, max_search_limit)  
                        # larger time frame 
    query_statement = """SELECT user_screen_name, text, ST_AsGeoJSON(coordinates)
                        from tweet_pgh 
                        WHERE created_at >= (now() - interval '30 days') 
                        limit %s; """ % (max_search_limit) 

    # Search entire db not just recent ones; very long query
    if minutes == None:
        query_statement = """SELECT user_screen_name, text, ST_AsGeoJSON(coordinates)
                        from tweet_pgh 
                        limit %s; """ % ( max_search_limit)

    # Search entire tweet_pgh
    # query_statement = """SELECT user_screen_name, text, ST_AsGeoJSON(coordinates)
    #                     from tweet_pgh 
    #                     WHERE created_at >= (now() - interval '%s minutes') ; """ % (minutes)

    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()
    cur.execute(query_statement)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    columns = ('screen_name', 'text', 'coordinates')
    all_recent_tweets = []
    for tweet in result:
        all_recent_tweets.append(dict(zip(columns,tweet)))
    for tweet in all_recent_tweets:
        tweet['coordinates'] = get_tweet_coordinates(tweet)
    return all_recent_tweets

def get_coords_of_venue(city="PGH", venue_id=None, venue_name=None):
    # if both venue_id and venue_name provided, searches by venue_id
    # returns (lat, long)
    if (city == "PGH"):
        city_state = 'pittsburgh,pa' 
    else:
        city_state = 'new+york+city,ny' 

    CLIENT_ID ='0015X0KQ1MLXKW0RTDOCOKUMACBCKE30ZY2IFYPCQDYTZ3EC'
    CLIENT_SECRET = 'UKJRW30YZAXC5DUO5KOZFPM4XWD3O3YSK0ANCZKB3TYCMCA5'
    url = 'https://api.foursquare.com/v2/venues/'
    city = 'near=%s' % ( city_state )

    client_id = 'client_id=' + CLIENT_ID
    client_secret = 'client_secret='+ CLIENT_SECRET
    today = "{:%Y%m%d}".format(datetime.now())
    date = 'v=%s' % ( today )# '&v=20150707' 

    # sample url request: 
    # https://api.foursquare.com/v2/venues/430d0a00f964a5203e271fe3?
    # oauth_token=SIVKZ0OBXJOO5DO3IJUZ2YDHGEBO4RCY3O3DVJTUE0IN1STQ&v=20150710

    # Query by venue id
    if venue_id != None:
        venue = '%s' %( venue_id )
        complete_url = url + venue + '?' + client_id + '&' + client_secret+'&' + date

    # https://api.foursquare.com/v2/venues/search?query=pittsburgh+
    # international+airport&match=true&near=pittsburgh,pa&oauth_token=SIVKZ0OBXJOO5DO3IJUZ2

    # Query by venue name- gets the top venue; may be not accurate.
    elif venue_name != None:
        url = 'https://api.foursquare.com/v2/venues/search?query='
        venue = venue_name.replace(' ', '+') 
        # url += 'search?match=true&limit=1'
        # complete_url = url + '&' + city + '&' + venue_name + '&' + client_id + '&' + client_secret+ '&' + date
        complete_url = url + venue + '&match=true&near=pittsburgh,pa&' + client_id + '&' + client_secret+ '&' + date
        print complete_url
    else: 

        print 'No venue specified.'
        return -1

    response = requests.get(complete_url)
    response = response.json()

    valid = response['meta']['code']
    if valid == 200:
        response = response['response']
        try: first_venue = response['venue']
        except: first_venue = response['venues'][0]
        print 'VENUE FOUND:'
        print first_venue
        first_venue_id = first_venue['id']
        first_venue_location = first_venue['location']
        keys = first_venue_location.keys()
        latitude = first_venue_location['lat']
        longitude = first_venue_location['lng']
        return [latitude, longitude]
    else: 
        print 'No valid venue found. Please check the venue again.'
        return -1

def get_tweet_coordinates(tweet):
    try: 
        coordinates = tweet['coordinates'] # gets a string 
        start_index = coordinates.find('[') + 1
        comma_index = coordinates.find(',', start_index)
        end_index = coordinates.find(']}')
        longitude = float(coordinates[start_index:comma_index])
        latitude = float(coordinates[comma_index+1:end_index])
        tweet_coordinates = [latitude, longitude]
        return tweet_coordinates
    except: 
        return 'Error: No coordinates found for given tweet'

def filter_by_venue(tweets, venue_id=None, venue_name=None ):
# Filters out tweets made more than max_distance away from given venue
    max_distance = .5  # miles
    city = "PGH"
    tweets_nearby = []
    venue_coordinates = get_coords_of_venue(city, 
                            venue_id= venue_id, venue_name= venue_name)
    for tweet in tweets:
        tweet_coordinates = tweet['coordinates']
        # distance = get_distance_in_feet(tweet_coordinates, venue_coordinates)
        distance = get_distance_in_miles(tweet_coordinates, venue_coordinates)
        if distance <= max_distance:
            tweets_nearby.append(tweet)
    return tweets_nearby

def filter_by_streets(tweets, streets):
# streets = ('Craig st', 'Forbes ave')
    max_distance = .5 # miles
    street_coords = get_street_coords(streets)
    tweets_nearby = []
    for tweet in tweets:
        tweet_coords = tweet['coordinates']
        # distance = get_distance_in_feet(street_coords, tweet_coords)
        distance = get_distance_in_miles(street_coords, tweet_coords)
        if distance <= max_distance:
            tweets_nearby.append(tweet)
    return tweets_nearby

def get_street_coords(tuple_of_streets):
# Takes in a tuple of street cross-section 
# Returns lat, lng points 
    street_a, street_b = tuple_of_streets[0], tuple_of_streets[1]
    street_a = street_a.replace(' ', '+')
    street_b = street_b.replace(' ', '+')
    address = street_a + '+' + street_b # Forbes+Ave+%26+S+Craig+St

    API_KEY = 'AIzaSyDmBsLXqP8ClEz8Rx_zK5-0Gow_TIMmWEQ'
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s,+Pittsburgh,+PA&key=%s' % (address, API_KEY)
    result = requests.get(url)
    result = result.json()
    result = result['results'][0]
    result = result['geometry']['location']
    lat, lng = result['lat'], result['lng']
    lat, lng = round(lat, 6), round(lng, 6)
    return (lat, lng)

def get_distance_in_miles(coordinate_a, coordinate_b):
    # also available in km, m, mi, ft, nm, nmi
    return vincenty(coordinate_a, coordinate_b).miles

def get_distance_in_feet(coordinate_a, coordinate_b):
    # also available in km, m, mi, ft, nm, nmi
    return vincenty(coordinate_a, coordinate_b).feet

def filter_by_home(tweets, neighborhood = None):
    for tweet in tweets:
        tweet = add_home(tweet)

    if neighborhood == None: 
        return tweets

    filtered = []
    for tweet in tweets:
        if tweet['home'] == neighborhood:
            filtered.append(tweet)
    return filtered

def add_home(tweet):
    # get username
    # get most common neighborhood
    # add to home key
    username = tweet['screen_name']
    query = "SELECT most_common_neighborhood FROM user_pgh WHERE screen_name = '%s' ;" % (username)
    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    if len(result) == 0: tweet['home'] = 'Not available.'
    else: tweet['home'] = result[0][0]
    return tweet



def filter_by_home_faster(tweets, neighborhood = None):
    if neighborhood == None: return tweets 

    query = "SELECT screen_name FROM user_pgh WHERE most_common_neighborhood = '%s' ;" % (neighborhood)
    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    result_flattened  = [item for sublist in result for item in sublist]

    for tweet in tweets:
        user = tweet['screen_name']
        if user not in result_flattened: tweets.remove(tweet)
        tweet['home'] = 'not added'

    return tweets

def remove_non_volunteers(tweets):
    # return tweets 
    for tweet in tweets:
        screen_name = tweet['screen_name']
        if is_a_volunteer(screen_name) == False:
            tweets.remove(tweet)
    return tweets

def is_a_volunteer(user_screen_name):
    return True ## for testing
    for volunteer in csv.reader(open("static/volunteers/screen-names.csv")):
        if volunteer[0] == user_screen_name:
            return True
    return False

# print filter_by_home([], 'Shadyside')
# print get_distance_in_miles((40.444187,-79.943345),(40.444187,-79.943345))
# print get_distance_in_miles((40.444187,-79.943345),(40.441126,-79.959336))
# print get_distance_in_miles((40.444187,-79.943345),(40.450887,-79.943024))
# print get_distance_in_miles((40.444187,-79.943345),(40.441238,-79.99473))
# print get_distance_in_miles((40.444187,-79.943345),(33.837399,-118.190292))



# FindUsers.search(last_tweet_venue_name ="Phipps Conservatory")
# SearchUsers.search(last_tweet_venue_name ="Phipps Conservatory")
# SearchUsers.search(last_tweet_venue_id ="40a55d80f964a52020f31ee3")
# SearchUsers.search(last_tweet_streets =("forbes ave", "craig st"))

# print SearchUsers.search(last_tweet_venue_name ="Carnegie Mellon University")
# print SearchUsers.search(last_tweet_venue_name ="Heinz Hall")
# print SearchUsers.search(last_tweet_venue_name ="US Steel Tower")

# print SearchUsers.search(last_tweet_streets =("7th st", "liberty ave"))

# print SearchUsers.search(last_tweet_venue_name ="Panera")
# print SearchUsers.search(last_tweet_venue_name ="Panear Bread")

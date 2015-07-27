#!/usr/bin/python

import string, psycopg2, requests, json, csv, time
from datetime import datetime, date
from geopy.distance import vincenty

Foursquare_CLIENT_ID = '0015X0KQ1MLXKW0RTDOCOKUMACBCKE30ZY2IFYPCQDYTZ3EC'
Foursquare_CLIENT_SECRET ='UKJRW30YZAXC5DUO5KOZFPM4XWD3O3YSK0ANCZKB3TYCMCA5'

class FindUsers():

    @staticmethod
    def search(  
                minutes_since = 5,
                home = None, 
                venue_id = None,
                venue_name = None,
                streets = None
        ): 
        result = {}
        query_start_time = time.time()
        recent_tweeters = get_recent_tweeters(minutes= minutes_since) 
        print 'RECENT TWEETERS:' 
        print recent_tweeters

        # result['total_recent_tweet_count'] = len(recent_tweeters)
        tweets_at_location = []
        if  venue_name != None: 
            tweets_at_location = filter_by_venue(users=recent_tweeters,
                                                venue_name=venue_name)
        elif venue_id != None:
            tweets_at_location = filter_by_venue(users=recent_tweeters, 
                                                venue_id= venue_id)
        elif streets != None:
            tweets_at_location = filter_by_streets(users=recent_tweeters,
                                                    streets=streets)
        else: 
            tweets_at_location = recent_tweeters

        print 'now home'
        if home != None:
            print 
            tweets_at_location = filter_by_home(users=tweets_at_location,  
                                                neighborhood=home)

        volunteers_at_location = get_volunteers(tweets_at_location)
        # result['search_result'] = matching_tweets 
        elapsed_time = time.time() - query_start_time
        # result['query_duration'] = str(elapsed_time)
        print '1234'
        print volunteers_at_location

        return volunteers_at_location

def get_recent_tweeters(minutes):
    print 'Making a request for users within ' + str(minutes) + ' minutes...' 
    query_statement = """SELECT DISTINCT ON (user_screen_name) user_screen_name, 
                        ST_AsGeoJSON(coordinates)
                        from tweet_pgh 
                        WHERE created_at >= (now() - interval '%s minutes') 
                        ORDER BY user_screen_name, created_at DESC; """ % (minutes)

    # FOR TESTING ONLY: Get first few hundred recent tweets for faster query. 
    max_search_limit = None
    if max_search_limit == None: max_search_limit = 150
    # 1. within x minutes
    query_statement = """SELECT DISTINCT ON (user_screen_name) user_screen_name, 
                        ST_AsGeoJSON(coordinates)
                        from tweet_pgh 
                        WHERE created_at >= (now() - interval '%s minutes') 
                        ORDER BY  user_screen_name, created_at DESC
                        limit %s; """ % (minutes, max_search_limit) 

    # 2. within x days
    # query_statement = """SELECT user_screen_name, ST_AsGeoJSON(coordinates)
    #                     from tweet_pgh 
    #                     WHERE created_at >= (now() - interval '30 days') 
    #                     limit %s; """ % (max_search_limit) 

    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()
    print query_statement
    cur.execute(query_statement)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    print 'got result!'

    columns = ('screen_name', 'coordinates')
    recent_tweeters = []
    for tweet in result:
        recent_tweeters.append( dict(zip(columns,tweet)) )
    for tweet in recent_tweeters:
        tweet['coordinates'] = get_tweet_coordinates(tweet) ### 
    return recent_tweeters

def filter_by_venue(users, venue_id=None, venue_name=None ):
    print 'filtering by benue ' + str(venue_id) + ' ' + str(venue_name)
    max_distance = 2000  # meters
    city = "PGH"
    users_nearby = []
    venue_coordinates = get_venue_coordinates(city=city, 
                            venue_id= venue_id, venue_name= venue_name)
    for user in users:
        user_coordinates = user['coordinates']
        print user_coordinates
        # distance = get_distance_in_feet(user_coordinates, venue_coordinates)
        distance = vincenty(user_coordinates, venue_coordinates).meters
        # distance = get_distance_in_miles(user_coordinates, venue_coordinates)
        print 'DISTANCE;'  + str(distance)
        if distance <= max_distance:
            users_nearby.append(user)
    print 'returning users_nearby'
    print users_nearby
    return users_nearby

def filter_by_streets(users, streets):
# streets = ('Craig st', 'Forbes ave')
    max_distance = 2000  # meters
    street_coords = get_street_coords(streets[0], streets[1])
    users_nearby = []
    for user in users:
        user_coords = user['coordinates']
        # distance = get_distance_in_feet(street_coords, tweet_coords)
        distance = vincenty(user_coords, street_coords).meters
        print distance
        if distance <= max_distance:
            users_nearby.append(user)
    return users_nearby

def filter_by_home(users, neighborhood):
    filtered = []
    print 'filtering home' + neighborhood
    for user in users:
        screen_name = user['screen_name']
        print screen_name
        home = get_home(screen_name)
        if (home == neighborhood): filtered.append(users)
    return filtered

def get_tweet_coordinates(tweet):
    print 'TWEET INSTANCE'
    print str(tweet)
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

def get_street_coords(street_a, street_b):
    print 'getting street coords'
    street_a = street_a.replace(' ', '+')
    street_b = street_b.replace(' ', '+')
    address = street_a + '+' + street_b # Forbes+Ave+%26+S+Craig+St

    API_KEY = 'AIzaSyDmBsLXqP8ClEz8Rx_zK5-0Gow_TIMmWEQ'
    url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s,+Pittsburgh,+PA&key=%s' % (address, API_KEY)

    # result = requests.get(url)
    # result = result.json()
    result = requests.get(url).json()
    print 'result: ' 
    print result 

    # result = result['results'][0]
    # result = result['geometry']['location']
    result = result['results'][0]['geometry']['location']

    lat, lng = result['lat'], result['lng']
    lat, lng = round(lat, 6), round(lng, 6)
    print (lat, lng)
    return (lat, lng)

def get_venue_coordinates(city="PGH", venue_id=None, venue_name=None):
    print 'getting venue coordinates'
    if (city == "PGH"): city_state = 'pittsburgh,pa' 
    else: city_state = 'new+york+city,ny' 
    url = 'https://api.foursquare.com/v2/venues/'
    city = 'near=%s' % ( city_state )

    # client_id = 'client_id=' + CLIENT_ID
    # client_secret = 'client_secret='+ CLIENT_SECRET
    today = "{:%Y%m%d}".format(datetime.now())
    date = 'v=%s' % ( today )# '&v=20150707' 
    print today + date

    # sample url request: 
    # https://api.foursquare.com/v2/venues/430d0a00f964a5203e271fe3?
    # oauth_token=SIVKZ0OBXJOO5DO3IJUZ2YDHGEBO4RCY3O3DVJTUE0IN1STQ&v=20150710

    # 430d0a00f964a5203e271fe3?
    # oauth_token=SIVKZ0OBXJOO5DO3IJUZ2YDHGEBO4RCY3O3DVJTUE0IN1STQ&v=20150710

    # Searches by venue_id by default if provided
    if venue_id != None:
        venue = '%s' %( venue_id )
        # complete_url = url + venue + '?' + client_id + '&' + client_secret+ '&' + date
        complete_url = 'https://api.foursquare.com/v2/venues/%s?client_id=%s&client_secret=%s&v=%s' %(venue_id, Foursquare_CLIENT_ID, Foursquare_CLIENT_SECRET, today)
        # https://api.foursquare.com/v2/venues/search?query=pittsburgh+
        # international+airport&match=true&near=pittsburgh,pa&oauth_token=SIVKZ0OBXJOO5DO3IJUZ2

    elif venue_name != None:
        url = 'https://api.foursquare.com/v2/venues/search?query='
        print 'name given'
        print venue_name
        venue = venue_name.replace(' ', '+') 
        # url += 'search?match=true&limit=1'
        # complete_url = url + '&' + city + '&' + venue_name + '&' + client_id + '&' + client_secret+ '&' + date
        # complete_url = url + venue + '&match=true&near=pittsburgh,pa&' + client_id + '&' + client_secret+ '&' + date
        complete_url = 'https://api.foursquare.com/v2/venues/search?query=%s&match=true&near=%s&client_id=%s&client_secret=%s&v=%s' %(venue, city_state, Foursquare_CLIENT_ID, Foursquare_CLIENT_SECRET, today)
        print complete_url
    else: 
        print 'No venue specified.'
        return -1

    response = requests.get(complete_url)
    response = response.json()

    valid = response['meta']['code']
    if valid == 200:
        print 'got venue coordinates'
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
        print [latitude, longitude]
        return [latitude, longitude]
    else: 
        print 'No valid venue found. Please check the venue again.'
        return -1



def get_home(screen_name):
    query = "SELECT most_common_neighborhood FROM user_pgh WHERE screen_name = '%s' ;" % (screen_name)
    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    if len(result) == 0: 
        return 'Home not available.'
    else: 
        home = result[0][0]
        print 'HOME: '
        print home
        return home

def get_volunteers(users):
    volunteers = []
    for user in users:
        screen_name = user['screen_name']
        if is_a_volunteer(screen_name) == True:
            volunteers.append(user)
    return volunteers

def is_a_volunteer(screen_name):
    return True ## for testing
    for volunteer in csv.reader(open("static/screen-names.csv")):
        if volunteer[0] == screen_name:
            return True
    return False



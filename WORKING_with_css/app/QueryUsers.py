#!/usr/bin/python

# QueryTwitterUsers is for querying for a list of twitter users (volunteers)
# who have just tweeted 
# and match one or more on the following criteria:
#   - home neighborhood
#   - home coordinate bounding box
#   - venue category (Foursquare) of last tweet (within a given timeframe)
#   - venue name / id (Foursquare) of last tweet (within a given timeframe)

import string, psycopg2, requests, json
from datetime import datetime, date
from geopy.distance import vincenty

def get_recent_tweets(minutes=5, max_num_tweets=5):
# Queries tweets made in the last minutes minutes from tweet_pgh db
# Return a list of tweets stored as dict
    query_statement = """SELECT user_screen_name, text, ST_AsGeoJSON(coordinates)
                        from tweet_pgh 
                        WHERE created_at >= (now() - interval '100000 minutes') 
                        limit 10 ; """
    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
    cur = conn.cursor()
    cur.execute(query_statement)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    columns = ('user_screen_name', 'text', 'coordinates')
    recent_tweets = []
    for tweet in result:
        recent_tweets.append(dict(zip(columns,tweet)))
    return recent_tweets


def get_coords_of_venue(city="PGH", venue_id=None, venue_name=None):
    # must provide either venue_id or venue_name.
    # if venue_id != venue_name, returns "error: two venue_id does not match venue_name"

    # search venue lat and long using its name on foursquare
    # returns (lat, long)
    if (city == "PGH"):
        city_state = 'pittsburgh,pa' 
    else:
        city_state = 'new+york+city,ny' # default

    CLIENT_ID ='0015X0KQ1MLXKW0RTDOCOKUMACBCKE30ZY2IFYPCQDYTZ3EC'
    CLIENT_SECRET = 'UKJRW30YZAXC5DUO5KOZFPM4XWD3O3YSK0ANCZKB3TYCMCA5'
    url = 'https://api.foursquare.com/v2/venues/'
    city = 'near=%s' % ( city_state)

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
        # complete_url = url + venue 
        # also check it matches venue_name ***

        # print complete_url

    # Query by venue name - not suggested. gets first result
    elif venue_name != None:
        venue = 'query=%s' % ( venue_name.replace(' ', '+') ) 
        url += 'search?match=true&limit=1'
        complete_url = url + '&' + city + '&' + venue_name + '&' + client_id + '&' + client_secret+ '&' + date
        # print complete_url

    else: 
        print 'No valid venue requested.'
        return

    # client_secret = '&client_secret='+ CLIENT_SECRET&v=YYYYMMDD
    # oauth_token = '%oauth_token=' + 'SIVKZ0OBXJOO5DO3IJUZ2YDHGEBO4RCY3O3DVJTUE0IN1STQ&v=20150707' 

    # print complete_url
    # url = 'https://api.foursquare.com/v2/venues/search?near=New+Delhi&intent=browse&radius=10000&limit=10&query=pizza+hut' + client_id + '&' + client_secret + '&v=20150707'
    
    response = requests.get(complete_url)
    response = response.json()


    # check the query is valid 
    # print response
    valid = response['meta']['code']
    if valid == 200:
        response = response['response']
        try: first_venue = response['venue']
        except: first_venue = response['venues'][0]
        # print first_venue
        first_venue_id = first_venue['id']
        first_venue_location = first_venue['location']
        keys = first_venue_location.keys()
        latitude = first_venue_location['lat']
        longitude = first_venue_location['lng']

        return (latitude, longitude)
    else: 
        print 'No location found. Please check the venue name'
        return -1

def get_tweet_coordinates(tweet):
    # print 'for tweet id: ' + tweet['id']
    try: 
        coordinates = tweet['coordinates'] # returns a string like:
                        # {"type":"Point","coordinates":[-79.933064,40.451525]}
        start_index = coordinates.find('[') + 1
        comma_index = coordinates.find(',', start_index)
        end_index = coordinates.find(']}')
        latitude = coordinates[start_index:comma_index]
        longitude = coordinates[comma_index+1:end_index]
        tweet_coordinates = (latitude, longitude)
        return tweet_coordinates

    except: 
        return 'Error: No coordinates found for given tweet'

def filter_venue(tweets, 
                venue_id=None, 
                venue_name=None ):
    max_distance = 10000  # miles

    # Gets an array of tweets and removes all that were not at the location / venue 
    city = "PGH"
    tweets_nearby = []
    # return tweets


    # 1. Get coordinates of the venue
        # a. if venue_id provided, find venue coords by id
        # b. if name provided, find venue coords by name

    venue_coordinates = get_coords_of_venue(city, 
                                            venue_id= venue_id, 
                                            venue_name= venue_name)
    for tweet in tweets:

        tweet_coordinates = get_tweet_coordinates(tweet)

        distance = get_distance_in_miles(tweet_coordinates, venue_coordinates)
        print 'DISTANCE = '
        print distance
        if distance < max_distance:
            tweets_nearby.append(tweet)
    print "returning tweets_nearby"
    return tweets_nearby

# def tweet_was_made_nearby(coordinate_a, coordinate_b):
def get_distance_in_miles(coordinate_a, coordinate_b):
    return vincenty(coordinate_a, coordinate_b).miles

def filter_home(tweets,
                neighborhood = None,
                coord_boxes = None):
    return tweets
class QueryTwitterUsers():

    @staticmethod
    def query(  
                home_neighborhood = None,
                home_coord_boxes = None,

                last_tweet_venue_type = None,
                last_tweet_venue_name = None,
                last_tweet_venue_id = None,

                last_tweet_streets = None,
            ):
        print 'querying' 

        # street / cross section ? 

        # 1. Get only recent tweets. 
        # 2. If last tweet location criteria selected, compare location
        # 3. If home criteria selected, compare home

        # Get all recent tweeters.
        recent_tweets = get_recent_tweets()

        # Filter by location.

        # Option 1: Venue
        if  (last_tweet_venue_name != None or last_tweet_venue_type != None or 
            last_tweet_venue_id != None):
            recent_tweets = filter_venue(   tweets= recent_tweets, 
                                            venue_id= last_tweet_venue_id,
                                            venue_name= last_tweet_venue_name)

        # Option 2: Streets
        elif last_tweet_streets != None:
            recent_tweets = filter_by_streets(   tweets= recent_tweets,
                                                streets= last_tweet_streets)

        # Filter by home.
        if home_neighborhood != None or home_coord_boxes != None:
            recent_tweets = filter_home(tweets= recent_tweets,  
                                        neighborhood = home_neighborhood,
                                        coord_boxes = home_coord_boxes)

        
        matched_users_and_last_tweets = recent_tweets
        print 'number found:'
        print len(matched_users_and_last_tweets)
        return matched_users_and_last_tweets


def test():
    print 'Testing get_coords_of_venue...'
    print( get_coords_of_venue('PGH', venue_id = '430d0a00f964a5203e271fe3') == (40.70227697066692, -73.9965033531189))
    print( get_coords_of_venue('PGH', venue_name='carnegie mellon cafe') == (40.440798744786015, -79.99699115753174))
    # assert( get_coords_of_venue('PGH', venue_name='carnegie mellon cafe'))
    # print( get_coords_of_venue('PGH', venue_id = '430d0a00f964a5203e271fe3'))


    print QueryTwitterUsers.query(last_tweet_venue_name = "carnegie mellon cafe")
    print QueryTwitterUsers.query(last_tweet_venue_id = "carnegie mellon cafe")
    print QueryTwitterUsers.query(last_tweet_venue_name = "carnegie mellon cafe")



    print 'Test passed!'

# print QueryTwitterUsers.query(last_tweet_venue_name = "carnegie mellon cafe")

# test()

def filter_by_streets(tweets, streets):
    max_distance = 0.01 # miles
    street_coords = get_street_coords(streets)
    tweets_nearby = []
    for tweet in tweets:
        tweet_coords = get_tweet_coordinates(tweet)
        if distance(street_coords, tweet_coords) < max_distance:
            tweets_nearby.append(tweet)
    return tweets_nearby

def get_street_coords(street_a, street_b):
# Takes in a tuple of street cross-section 
# Returns lat, lng points 

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

def test_get_street_coords():
    assert (get_street_coords("Forbes ave", "craig st") == (40.444535, -79.948752))
# test_get_street_coords()



# Unused:
# def filter_venue_name(tweets, venue_name):
#     venue_coordinates = get_coords_of_venue(venue=v_name)
#     for tweet in tweets:
#         tweet_coordinates = get_twitter_coordinates(tweet)
#         if near(venue_coordinates, tweet_coordinates) == True:
#             filtered_tweets.append(tweet)
#         else:
#             pass

def test_get_street_coords():
    assert (get_street_coords("Forbes ave", "craig st") == (40.444535, -79.948752))
    assert (get_street_coords("fifth ave", "forbes ave") == (40.349759, -79.874535) )
test_get_street_coords()


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

# Unused:
# def filter_by_venue_name(tweets, venue_name):
#     venue_coordinates = get_coords_of_venue(venue=v_name)
#     for tweet in tweets:
#         tweet_coordinates = get_twitter_coordinates(tweet)
#         if near(venue_coordinates, tweet_coordinates) == True:
#             filtered_tweets.append(tweet)
#         else:
#             pass




# FindUsers is for querying for a list of twitter users (volunteers)
# who have just tweeted 
# and match one or more on the following criteria:
#   - home neighborhood
#   - home coordinate bounding box
#   - venue category (Foursquare) of last tweet (within a given timeframe)
#   - venue name / id (Foursquare) of last tweet (within a given timeframe)


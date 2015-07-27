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
    return results

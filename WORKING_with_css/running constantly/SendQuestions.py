
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
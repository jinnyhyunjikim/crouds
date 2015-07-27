#!/usr/bin/python

import psycopg2

class GetResponses():

	@staticmethod
	def get_responses():
	    print 'getting parsed responses'
	    conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
	    cur = conn.cursor()

	    statement = """SELECT response_id, response_parsed, question.location, question.subject, user_id, to_char(sent_at, 'Day'), to_char(sent_at, 'HH12:MI AM')
	    FROM question_response 
	    INNER JOIN question ON question.question_id = question_response.question_id
	    ORDER BY question.question_id DESC ; """
	    print statement
	    cur.execute(statement)
	    responses = cur.fetchall()
	    conn.commit()
	    cur.close()
	    conn.close()

	    responses_list = [] # will insert each dictionary here
	    print 'getting questions 2'
	    columns = ('response_id', 'response_parsed', 'location', 'subject', 'username', 'day', 'time') 
	    for response in responses:
	        responses_list.append(dict(zip (columns, response)))

	    # for response in responses_list:

	    print 'RESPONSES PARSED ==='
	    print responses_list
	    return responses_list
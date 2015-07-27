#!/usr/bin/python

import psycopg2

def sendTweet(user_to_ask, question_text):
    question_statement = "@" + user_to_ask + " " + question_text # e.g. '@jinny6235 Good afternoon!'
    print "SEDING TWEET!" + question_statement
    twitter.update_status(status = question_statement) # send tweet

    print " TWEET sent: " + user_to_ask + "!"
    print "updated database: QUESTION_TWEET"


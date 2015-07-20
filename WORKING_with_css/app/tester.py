#!/usr/bin/python

import csv
from ParseTweet import *
# For testing functions used in QueryUsers.py

tests_passed = tests_failed = 0

for line in csv.reader(open("tester-files/tests-parser.csv")):
	if line[0] == "number":
		returned = ParseTweet.parse(line[1]) 
		returned = str(returned)

	elif line[0] == "mc":
		returned = ParseTweet.get_multiple_choice_answer(line[1])

	else:
		continue

	expected = line[2]
	if (returned == expected):
		tests_passed += 1
	else:
		tests_failed += 1
		print "this test failed for %s -  %s, expected %s, returned %s" % (line[0], line[1], line[2],returned)

print "Passed: " + str(tests_passed) 
print "Failed: " + str(tests_failed)



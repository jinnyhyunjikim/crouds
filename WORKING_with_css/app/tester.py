#!/usr/bin/python

import csv
from ParseTweet import *
# For testing functions used in QueryUsers.py

tests_passed = tests_failed = 0

for line in csv.reader(open("tester-files/tests-parser.csv")):
	if line[0] == "number":
		returned = ParseTweet.parse(type='number', str=line[1]) 
		returned = str(returned)

	elif line[0] == "mc":
		returned = ParseTweet.parse(type='mc', str=line[1])

	else:
		continue

	expected = line[2]
	if (returned == expected):
		tests_passed += 1
		print "Successfully parsed! \nResponse: \n\t%s, EXPECTED =  %s, PARSED = %s" % (line[1], line[2],returned)
	else:
		tests_failed += 1
		print "this test failed for <%s> \n\t%s, expected %s, returned %s" % (line[0], line[1], line[2],returned)

print "Passed: " + str(tests_passed) 
print "Failed: " + str(tests_failed)



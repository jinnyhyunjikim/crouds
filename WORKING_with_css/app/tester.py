#!/usr/bin/python

import csv
from Parser import *
# For testing functions used in QueryUsers.py

tests_passed = tests_failed = 0
for line in csv.reader(open("tester-files/tests-parser.csv")):

    returned = Parser.get_one_integer(line[0]) 
    returned = str(returned)
    expected = line[1]
    if (returned == expected):
        tests_passed += 1
    else:
        tests_failed += 1
        print "this test failed for string %s, expected %s, returned %s" % (line[0], line[1], returned)

print "Passed: " + str(tests_passed) 
print "Failed: " + str(tests_failed)
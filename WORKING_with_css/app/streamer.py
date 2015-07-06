#!/usr/bin/env python
from twython import Twython
from twython import TwythonStreamer 
import json
import string
import psycopg2

# Initialize Twython for Twitter user streaming, using OAuth1

# <========== Use OAuth2 ==========> #
# twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
# ACCESS_TOKEN = twitter.obtain_access_token()
# twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
# <========== End Using OAuth2 ==========> #

# <========== Use OAuth1 ==========> #
APP_KEY = 'UmLjRKeW4Gc9RlLUBqoNfpmyG'
APP_SECRET = 'qFCKEMZbLD7NO4ki2ksbibQ01SV88ECJQLZn3TQmQXiJkvN877'
ACCESS_TOKEN = '3307752328-R52HmpgczQt5tl8hYohaXZ9j0moNMOfAemNEdd1'
ACCESS_TOKEN_SECRET = 'eJNVo321y9Ancj08oJOo9Ii4KFHJIJgbyFSgaRuMGHb3x'

twitter = Twython(APP_KEY, APP_SECRET,
				  ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# twitter.verify_credentials()
# <========== End Using OAuth1 ==========> #

def getTweetId(tweetData):
	if 'id' in tweetData: 
		tweet_unique_id = str(tweetData['id'])
		return tweet_unique_id
	else:
		print "no tweet unique id"
		return -1

def getUserMention_username(tweet_data):
	if 'user_mentions' in tweetData:
		user_mention_username = str(tweetData['user']['name'])
		print 'mention username:  ' + user_mention_username
		return user_mention_username
	else: 
		print 'no user mention in data'

def getUser(tweetData):
	if 'user' in tweetData: 
		username = str(tweetData['user']['id_str'])
		print "username: " + username
		return str(username)
	else:
		print "no username"
		return -1

def getDate(tweetData):
	if 'created_at' in tweetData: 
		dateAndTime = tweetData['created_at']
		date = extractDate(dateAndTime)
		return date
	else:
		print "no date"
		return -1

def extractDate(date_and_time_str):  # needs improvement
	return date_and_time_str[:10]

def extractTime(date_and_time_str):  # needs improvement
	return date_and_time_str[10:]

def getTime(tweetData):
	if 'created_at' in tweetData: 
		dateAndTime = tweetData['created_at']
		time = extractTime(dateAndTime)
		return time
	else:
		print "no create at"
		return -1 

def getResponseText(tweetData):
	if 'text' in tweetData:
		text = tweetData['text'].encode('utf-8')
		return text
	else:
		print 'no response text'
		return -1

def parseResponse(response_text):
# Takes in a string and extracts a number if present.
# Returns -1 otherwise.
# See test_parseResposne below.
	array_of_words = splitText(response_text)
	words_in_numbers = convertWordsToNumbers(array_of_words)
	words_in_numbers = combineTwoNumbersNextToEachOther(words_in_numbers)
	non_negative_numbers = deleteNegativeNumbers(words_in_numbers)
	print "NON NEG NUMBERS" 
	print non_negative_numbers
	count = extracted_numbers_count = len(non_negative_numbers)
	if (count  == 0 or count > 2): return None # return 'Error parsing text'
	if (count == 1): return non_negative_numbers[0]
	if (count == 2): 
		return (non_negative_numbers[0] + non_negative_numbers[1]) / 2

def splitText(string):
	return string.split()

def convertWordsToNumbers(array_of_words_and_numbers):    
# ['maybe', 'two', 'to', '5'] -> [-1, 2, -1, 5]
# ['thirty', 'two', 'I','think'] -> [30, 2, -1, -1]
# ['I', 'don't', 'know'] -> [-1, -1, -1]
# [] -> []

# Does not support errors, misspellings, and decimals 
#       e.g. ['around', 'thirty?'] -> [-1, -1] -> [-1, 30]   
#       e.g. ['around', 'thirtee'] -> [-1, -1] -> [-1, 30]  
	
	array_of_numbers = []   

	for item in array_of_words_and_numbers:
		item = removePunctuationInAWord(item)  
		number = convertWordToNumber(item)

		array_of_numbers.append(number)

	return array_of_numbers

def convertWordToNumber(word_or_number):
# Takes in a string without whitespace and punctuation 
# Returns a number if it either already is a number or is a number spelled out in text
	
	if word_or_number.lower() == "none": return 0
	try:        # Item is already a number. Convert to int
		number = int(word_or_number)
	except:     # Item is not a number. Read if it is a number spelled out.
		number = text_to_int_method_1(word_or_number)
	return number 

def removePunctuationInAWord(word):
# Takes in a string with no whitespace and removes all punctuation marks. 
	word_without_punctuation = ""
	for i in xrange( len(word) ):
		if word[i] not in string.punctuation:
			word_without_punctuation += word[i]
	return word_without_punctuation
	

	
def combineTwoNumbersNextToEachOther(array_of_numbers):
# Takes in an array of numbers and if two non-negative numbers are consecutive 
# and the first one is a multiple of ten and the second a value less than ten combine the two. 
# e.g. [-1, -1, 20, 3] -> [-1, -1, 23]
#      [20, 30, 4] -> [20, 34]
#      [20, 30, 14] -> [20, 30, 14]
#      [12, 3, 10] -> [12, 3, 10]
#      [12, -3, 10] -> [12, -3, 10]
	new_array = []
	number_count = len(array_of_numbers)
	i = 0 
	while (i < number_count):
		number = array_of_numbers[i]
		if (number != -1 and number % 10 == 0
			and i + 1 < number_count and array_of_numbers[i + 1] != -1 and
			array_of_numbers[i + 1] < 10):
			combined_number = array_of_numbers[i] + array_of_numbers[i + 1] 
			new_array.append(combined_number) 
			i += 2
		else:
			new_array.append(number)
			i += 1
	return new_array

def deleteNegativeNumbers(array_of_numbers):
# Takes in an array of zero and non-zero numbers 
# Returns a new array copying only non-negative numbers
	new_array = []
	for n in array_of_numbers:
		if n >= 0:
			new_array.append(n)
	return new_array

def getQuestionID(tweet_text):
# Takes in a tweet sent from self, e.g. '@jinny6235 How many trucks do you 
# see on Craig+Forbes right now?'
# Returns the question_id corresponding to the question in question db
# Returns -1 if no such question exists
	
	# remove destination handle, e.g. @pgh_resident
	question_text = removeUserMentions(tweet_text)

	# get id of question in question db by searching its text

	print ("! connecting: GETTING QUESTION ID  ! ")
	conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
	cur = conn.cursor()

	# Method 1: Exact text comparison
	print question_text
	statement = "SELECT question_id FROM question WHERE question_text = '%s' ORDER BY created_at DESC ;"  %(question_text)

	# Method 2: Using LIKE
	# ex) WHERE pname LIKE '%gizmo%'
	question_text = "%" + question_text + "%"
	question_text = question_text + "%"
	# statement = "SELECT question_id FROM question WHERE question_text LIKE '%s' ;"  %(question_text) 
	cur.execute(statement)
	conn.commit()
	top_question = cur.fetchall()[0]
	top_question_id = top_question[0]
	# there may be many questions asked at different times. 
	# fetch the latest one. 

	print "top question id matching"
	print top_question_id
	print "-- Done searching: QUESTION ID ! now returning--"
	return top_question_id
	# what if no matching id?

def test_getQuestionID():
	print "Testing getQuestionID..."
	assert (getQuestionID("@pgher How many trucks do you see on Craig+Forbes right now?") == 3)
	assert (getQuestionID("@pgher2 How many trucks do you see on Craig+Forbes right now?") == 3)
	assert (getQuestionID("@pgher2 Have a nice weekend!") == -1)
	print "Passed!"

def text_to_int_method_1(textnum, numwords={}):
# Source: http://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers-python
	if not numwords:
	  units = [
		"zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
		"nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
		"sixteen", "seventeen", "eighteen", "nineteen",
	  ]

	  tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

	  scales = ["hundred", "thousand", "million", "billion", "trillion"]

	  # numwords["and"] = (1, 0) # un-comment for recognition of the word "and"

	  for idx, word in enumerate(units):    numwords[word] = (1, idx)
	  for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
	  for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

	current = result = 0
	for word in textnum.split():
		if word not in numwords:
			return -1
		  # raise Exception("Illegal word: " + word)

		scale, increment = numwords[word]
		current = current * scale + increment
		if scale > 100:
			result += current
			current = 0
	return result + current

def getQuestionTweetID(user_id):
# Takes in a twitter user id and find a question_tweet with an open question
# and corresponding user_id
	return 1
	

def byteify(input):
# Source: http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead
# -of-unicode-ones-from-json-in-python
	if isinstance(input, dict):
		return {byteify(key):byteify(value) for key,value in input.iteritems()}
	elif isinstance(input, list):
		return [byteify(element) for element in input]
	elif isinstance(input, unicode):
		return input.encode('utf-8')
	else:
		return input


class UserStreamer(TwythonStreamer):
	def on_success(self, data):
	# Receiving twitter stream from an account (followers' tweets)
		# print json.dumps(data, indent=4, sort_keys=True) # to pretty-print
		print "here"
		print data

		if 'user' in data: # Check that it's a tweet data, not user data
			user = data['user']['id']
			print "got user"
			print user
			data = json.dumps(data)
			data = json.loads(data)
			data = byteify(data) 
			# print data

			_MY_USER_ID_ =  3307752328 # 2875905140
			_MY_SCREEN_NAME_ = 'jinny6235' # 'jinnyhyunjikim'

			# It's a tweet replying to me.
			if data['in_reply_to_user_id'] == _MY_USER_ID_:
				# print "it's a tweet repying to me !"
				print "hereeeee id"
				tweet_id = data['id'] #prob stringify
				# tweet_id = int( data['id'] ) #prob stringify
				tweet_replying_to = data['in_reply_to_status_id']
				if tweet_replying_to == None: 
					tweet_replying_to = -1 # indicates the original question_tweet was deleted
				reply = data['text'] 
				reply = reply_without_my_id = removeUserMentions(reply)
				parsed = parseResponse(reply)
				print "PARSED: "
				print parsed
				user_screen_name = data['user']['screen_name']
				created_at = data['created_at']

				if reply == None: reply = "None" # Can't add None objects to postgresql db
				if parsed == None: parsed = -1
				updateDatabase("question_response", tweet_id, reply, parsed,
									 tweet_replying_to, user_screen_name, created_at)
				print "db updated! reply"

			# It's a tweet I'm sending out
			elif data['user']['screen_name'] == _MY_SCREEN_NAME_:
				tweet_id = data['id'] #prob stringify
				print "hereeeee id"
				question = data['text']
				question_id = getQuestionID(question)
				# user_asked = data['entities']['user_mentions'][0]['screen_name'] # what if no user_mentions?
				# print data['entities']['user_mentions'][0] # what if no user_mentions?
				user_asked = data['entities']['user_mentions'][0]['screen_name'] # what if no user_mentions?
				updateDatabase("question_tweet", tweet_id, question_id, user_asked) 
				print "db updated! sending out"

			else: 
				print "not relevant tweet"
		# If neither, ignore. 
		else: 
			print "tried but failed"

	def on_error(self, status_code, data):
		print "code" + str(status_code)

		# Want to stop trying to get data because of the error?
		# Uncomment the next line!
		# self.disconnect()


def removeUserMentions(text):
# Takes in a tweet text, e.g. "@crouds_bot I see 23."
# Returns text with user mentions removed.

	# 1. Check if first word starts with "@"
	# 2. If yes, remove that word
	text_as_list = string.split(text)
	if len(text_as_list) > 0:
		first_word = text_as_list[0]
		if first_word[:1] == "@":
			text_as_list = text_as_list[1:]
			back_as_one_string = " ".join(text_as_list)
			return back_as_one_string
	return text


def getNextRowID(tablename):
	# Connect to response table in the database
	conn = psycopg2.connect("dbname=tweet user=jinnyhyunjikim")
	cur = conn.cursor()

	# Query the response_id of the last element 
	if tablename == 'question_response':
		query = "SELECT max(response_id) FROM question_response;"
	elif tablename == 'question':
		query = "SELECT max(question_id) FROM question;"
	elif tablename == 'question_user':
		query = "SELECT max(user_id) FROM question_user;"
	elif tablename == 'question_response':
		query = "SELECT max(response_id) FROM response_id;"
	else:
		print "Error: No such table in psql tweet database."

	cur.execute(query)
	top_element_response_id = cur.fetchone()[0]

	# Return next number
	if top_element_response_id == None: return 0
	return top_element_response_id + 1


def updateDatabase(tablename, *data):
	COLUMNS_question = '(question_id, topic, question_text, expected_response_type, venue, city, created_at, expires_at)'
	COLUMNS_question_user = '(user_id)'
	COLUMNS_response = '(response_id, response_raw, response_parsed, in_reply_to, user_id, created_at)'
	COLUMNS_question_tweet = '(tweet_id, question_id, user_id)'


	print ("! connecting ! ")
	conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
	cur = conn.cursor()

	print "--Updating database-- "
	# row_id = getNextRowID(tablename)
	TABLE_NAME = tablename
	print 'VALUES -->> ' + str(data) 
	data = list(data) # convert tuple to list
	# data.insert(0, row_id) # add row id
	data = tuple(data) 
	VALUES = str(data)
	# VALUES_question = '(%d, %s, %s, %s, %s, %d, %s )' % (data)
	# VALUES_question_tweet = '(%d, %s, %s, %s, %s, %d, %s )' % (data)

	if tablename == 'question_response':
		COLUMNS = str(COLUMNS_response)
	elif tablename == 'question':
		COLUMNS = str(COLUMNS_question)  
	elif tablename == 'question_user':
		COLUMNS = str(COLUMNS_question_user)
	elif tablename == 'question_tweet':
		COLUMNS = str(COLUMNS_question_tweet)
	else:
		print "Error: No such table to update!"


	statement = "INSERT INTO " + TABLE_NAME + " " + COLUMNS + " VALUES " + VALUES + ";"
	print "statement = " +  statement
	cur.execute(statement)
	conn.commit()
	print "--Added to database!--"



#search
# print stream.statuses.filter(track='@twitter')

# print stream.statuses.filter()
print "dfsd"
# print  stream.user()
## Make it stop streaming? 

# +++++++++++++++++++++++

# try:
#     user_timeline = twitter.get_user_timeline(screen_name='jinny6235')
#     # user_timeline = twitter.get_user_timeline()
# except TwythonError as e:
#     print "error" + e

# print "here" + user_timeline


# +++++++++++++++++++++++







class CROUDS:
	def __init__(self):

		APP_KEY = '5vPCWuBGcXyzpMYswm0GVgs8b'
		APP_SECRET = '8V9Pk9BVudI6GceaVNWo1HupJsXokKATK94bwZcom47SQf5KGS'
		ACCESS_TOKEN = '2875905140-02P20c7dHFDgb9yIE2jEqdlidS9xOGkdVq4nrGB'
		ACCESS_TOKEN_SECRET = '42azhlc7p4Hi949NvPth3FmdJ8bZafzGqLIrAHKTXDOSi'
		self.twitter = Twython(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
		self.stream = UserStreamer(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
		self.users_to_ask = []
		self.question = ""

	# def getUsersToAsk(city, venue, how_many, type):
	def getUsersToAsk(venue = "Kennywood Park"):
	# Looks at tweets from last 5 / 10 / 15 minutes and returns list of 
	# users identified to be at desired venue / location

	# city = pgh, ny, sf, boston, 
	# type = "near" or "at". currently only supporting "at"
	# venue needs to be spelled and capitalized correctly

		_city_ = "tweet_pgh"
		_search_limit_ = 100
		query = """SELECT DISTINCT user_screen_name FROM %s 
					WHERE created_at >= (now() - interval '5 minutes') 
					AND place-> 'full_name' = '%s' limit %d""" % (_city_, "Kennywood Park", _search_limit_) 
		print query

		# Access postsql tweet db  
		print ("connecting")
		# conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim", password="jinny6235", host="54.211.203.96", port="5432", connect_timeout=33)
		conn = psycopg2.connect(database="tweet", user="jinnyhyunjikim")
		cur = conn.cursor()

		# Insert
		print "--Accessing database-- "
		cur.execute(query)
		result = cur.fetchone()
		print result
		conn.commit()
		cur.close()
		conn.close()
		print "--Added to database!--"
		return result


	def asking(self):
		# Get question
		# twitter = initialize_twitter(self)

		def getQuestion():
			return "Initial question?"


		def askQuestion(twitter, users_to_ask, question):
				for user in users_to_ask:
					sendTweet(twitter, user, question)
					# updateDatabase("question_tweet", )
					# updateDatabase_question_tweet(user, question)

				# update table question

		def sendTweet( twitter, user_to_ask, question_text):
			question_statement = user_to_ask + " " + question_text # e.g. '@jinny6235 Good afternoon!'
			twitter.update_status(status = question_statement)

			print " Question sent: " + user_to_ask + "!"

		# question = getQuestion()
		# users_to_ask = getUsersToAsk()
		# askQuestion(twitter, users_to_ask, question)

	

	def stream_twitter_feed(self):
		streaming = self.stream.user()







# stream = crouds.initialize()
# print crouds.getUsersToAsk()
# crouds.asking()
# print 'sending question'
# twitter = crouds.initialize_twitter()
# print crouds.sendQuestion(twitter)











crouds = CROUDS()
print "running"
crouds.stream_twitter_feed()






#  Testing  
def test_combineTwoNumbersNextToEachOther():
	print 'Testing combineTwoNumbersNextToEachOther...'
	assert (combineTwoNumbersNextToEachOther([20, 3, -1]) == [23, -1])
	assert (combineTwoNumbersNextToEachOther([20, -1, -1]) == [20, -1, -1])
	assert (combineTwoNumbersNextToEachOther([]) == [])
	assert (combineTwoNumbersNextToEachOther([0]) == [0])
	assert (combineTwoNumbersNextToEachOther([-1, -1, 3]) == [-1, -1, 3])
	assert (combineTwoNumbersNextToEachOther([-1, -1, 30]) == [-1, -1, 30])
	assert (combineTwoNumbersNextToEachOther([-1, 10, 2, 20]) == [-1, 12, 20])
	assert (combineTwoNumbersNextToEachOther([-1, 10, 2, 20, 3]) == [-1, 12, 23])
	print 'Test passed!'

def test_deleteNegativeNumbers():
	print 'Testing deleteNegativeNumbers...'
	assert (deleteNegativeNumbers([23, -1]) == [23])
	assert (deleteNegativeNumbers([20, -1, -1]) == [20])
	assert (deleteNegativeNumbers([]) == [])
	assert (deleteNegativeNumbers([0]) == [0])
	assert (deleteNegativeNumbers([0, 0, 10]) == [0, 0, 10])
	assert (deleteNegativeNumbers([-1, -1, 3]) == [3])
	assert (deleteNegativeNumbers([-1, -1, 30]) == [30])
	assert (deleteNegativeNumbers([-1, 10, 2, -1, 20]) == [10, 2, 20] )
	assert (deleteNegativeNumbers([-13, 12, 23]) == [12, 23])
	print 'Test passed!'

def test_removePunctuationInAWord():
	print "Testing removePunctuationInAWord..."
	assert( removePunctuationInAWord("~5.") == "5")
	assert( removePunctuationInAWord(".") == "")
	assert( removePunctuationInAWord("1,200.") == "1200")
	assert( removePunctuationInAWord("13....,") == "13")
	assert( removePunctuationInAWord("13....,") == "13")
	assert( removePunctuationInAWord("(13.)") == "13")
	print "Test passed !"

def test_parseResponse():
	print 'Testing parseResponse...'
	assert (parseResponse("23 minutes") == 23)
	assert (parseResponse("around 23 minutes") == 23)
	assert (parseResponse("idk") == None)
	assert (parseResponse("") == None)
	assert (parseResponse("around 16 to 20 cars") == 18)
	assert (parseResponse("about twenty cars") == 20)
	assert (parseResponse("about thirty three cars") == 33)

	assert (parseResponse("maybe seventeen") == 17)
	assert (parseResponse("about twenty to 30 cars") == 25)
	assert (parseResponse("almost ten") == 10)
	assert (parseResponse("  2") == 2)
	assert (parseResponse("I see none") == 0) # "none" read as 0
	assert (parseResponse("None.") == 0) # "none" read as 0
	# assert (parseResponse("about thirty-three cars") == 33) # not yet supported
	# assert (parseResponse("about thirtythree cars") == 33)
	# assert (parseResponse("around 15 to 20 cars") == 18) # float avg not yet supported
	# assert (parseResponse("around23 minutes") == 23) # not yet supported
	print 'Test passed!'

def test_removeUserMentions():
	print "Testing removeUserMentions..."
	assert (removeUserMentions("@crouds_bot I see 23.") == "I see 23.")
	assert (removeUserMentions("@20_5 30-40.") == "30-40.")
	assert (removeUserMentions("around 23?") == "around 23?")
	assert (removeUserMentions("") == "")
	assert (removeUserMentions(" ") == " ")
	print "Passed!"

def __test__():
	print "#### Testing ######"
	test_removePunctuationInAWord()
	test_combineTwoNumbersNextToEachOther()
	test_deleteNegativeNumbers()
	test_parseResponse()
	test_removeUserMentions()
	print "#### End of Tests ######"


# __test__()
# <========== End Test Functions ==========> #


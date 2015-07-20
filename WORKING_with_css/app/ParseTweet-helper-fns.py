# Test fn's for ParseTweet helpter fn's

    """Assumes n is a positive integer. Returns error if not."
assert spoken_word_to_number_method_1('') == None
assert spoken_word_to_number_method_1('one hundred') == 100
assert spoken_word_to_number_method_1('eleven') == 11
assert spoken_word_to_number_method_1('twenty two') == 22
assert spoken_word_to_number_method_1('thirty-two') == 32
assert spoken_word_to_number_method_1('forty two') == 42
assert spoken_word_to_number_method_1('two hundred thirty two') == 232
assert spoken_word_to_number_method_1('two thirty two') == 232
assert spoken_word_to_number_method_1('nineteen hundred eighty nine') == 1989
assert spoken_word_to_number_method_1('nineteen eighty nine') == 1989
assert spoken_word_to_number_method_1('one thousand nine hundred and eighty nine') == 1989
assert spoken_word_to_number_method_1('nine eighty') == 980
assert spoken_word_to_number_method_1('nine two') == 92 # wont be able to convert this one
assert spoken_word_to_number_method_1('nine thousand nine hundred') == 9900
assert spoken_word_to_number_method_1('one thousand nine hundred one') == 1901
# assert spoken_word_to_number_method_1('light') # KeyError
# assert spoken_word_to_number_method_1('twentee-one') # KeyError
"""
    """
print "Testing convert_word_to_number..."
assert( convert_word_to_numbers(['maybe', 'two', 'to', '5']) == [-1, 2, -1, 5]) 
assert( convert_word_to_numbers([]) == []) 
assert( convert_word_to_numbers(['']) == [-1]) 
assert( convert_word_to_numbers(['none']) == [0]) 
assert( convert_word_to_numbers(['thirty', 'two', 'I','think']) == [30, 2, -1, -1]) 
assert( convert_word_to_numbers(['I', 'don't', 'know']) == [-1, -1, -1])
assert( convert_word_to_numbers(['thirteen']) == [13])
assert( convert_word_to_numbers("thirty-five and six") == [35, -1, 6])
print "Test passed !"
""" 
    """
print "Testing convert_word_to_number..."
assert( convert_word_to_number("") == -1) 
assert( convert_word_to_number("any") == 0) 
assert( convert_word_to_number("none") == 0) 
assert( convert_word_to_number("this") == -1)
assert( convert_word_to_number("thirteen") == 13)
assert( convert_word_to_number("thirty-five") == 35)
assert( convert_word_to_number("1200") == 1200)
assert( convert_word_to_number("13") == 13)
print "Test passed !"
""" 

    """
print "Testing right_strip_punctuation..."
assert( right_strip_punctuation("~5.") == "~5") # edge case
assert( right_strip_punctuation(".") == "")
assert( right_strip_punctuation("1,200.") == "1,200")
assert( right_strip_punctuation("13....,") == "13")
assert( right_strip_punctuation("(13.)") == "(13")
print "Test passed !"
""" 

    """
print "Testing left_strip_punctuation..."
assert( left_strip_punctuation("~5.") == "~5") # edge case
assert( left_strip_punctuation(".") == "")
assert( left_strip_punctuation("1,200.") == "1,200.")
assert( left_strip_punctuation("%13..") == "13..")
assert( left_strip_punctuation("13.)") == "(13.)")
assert( left_strip_punctuation("13") == "13")
print "Test passed !"
"""

    """
print 'Testing combine_two_numbers_next_to_each_other...'
assert (combine_two_numbers_next_to_each_other([20, 3, -1]) == [23, -1])
assert (combine_two_numbers_next_to_each_other([20, -1, -1]) == [20, -1, -1])
assert (combine_two_numbers_next_to_each_other([]) == [])
assert (combine_two_numbers_next_to_each_other([0]) == [0])
assert (combine_two_numbers_next_to_each_other([-1, -1, 3]) == [-1, -1, 3])
assert (combine_two_numbers_next_to_each_other([-1, -1, 30]) == [-1, -1, 30])
assert (combine_two_numbers_next_to_each_other([-1, 10, 2, 20]) == [-1, 12, 20])
print 'Test passed!'
"""

    """
print 'Testing remove_negative_numbers...'
assert (remove_negative_numbers([20, 3]) == [20, 3])
assert (remove_negative_numbers([20, -1, -1]) == [20])
assert (remove_negative_numbers([]) == [])
assert (remove_negative_numbers([0]) == [0])
assert (remove_negative_numbers([-1, -1, 3]) == [3])
assert (remove_negative_numbers([1, -10, 2, 20]) == [1, 12, 20])
print 'Test passed!'
"""
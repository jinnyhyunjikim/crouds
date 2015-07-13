#############################################
# spoken_word_to_number_method_2
#############################################

# Source: http://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers-python
def spoken_word_to_number_method_2(textnum, numwords={}):
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

def test_spoken_word_to_number_method_2():
    print 'Testing spoken_word_to_number_method_2'
    assert (spoken_word_to_number_method_2("one") == 1)
    assert (spoken_word_to_number_method_2("thirty one") == 31)
    assert (spoken_word_to_number_method_2("twelve") == 12)
    assert (spoken_word_to_number_method_2("twelve ") == 12)
    assert (spoken_word_to_number_method_2("ten") == 10)
    assert (spoken_word_to_number_method_2("one hundred") == 100)
    assert (spoken_word_to_number_method_2("two hundred") == 200)
    assert (spoken_word_to_number_method_2("two hundred thirty one") == 231)
    assert (spoken_word_to_number_method_2("forty") == 40)
    assert (spoken_word_to_number_method_2("forty two") == 42)
    # print spoken_word_to_number_method_2("fortytwo")
    # assert (spoken_word_to_number_method_2("fortytwo") == 42)
    # assert (spoken_word_to_number_method_2("forty-two") == 42)
    print 'Test passed!'
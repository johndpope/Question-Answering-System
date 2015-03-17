#!/usr/bin/python
#
# sentence_util.py
#

from collections import deque;
from copy import deepcopy;
from util.tagUtil import *
from util.wordUtil import WordIdentity
import nltk;

# Minimum number of tokens required in a sentence to turn it into a question
MIN_SENTENCE_LENGTH = 5

# Returns True if the string s can reasonably be described as a sentence
# The metrics we define for qualified "sentence" are:
# 1. longer or equal to minimum length
# 2. contain a verb
# 3. has end punctuation
def is_sentence(s):
    # Get the tokens of the sentence.  It's possible there are none,
    # in which case this is definitely not a sentence.
    toks = nltk.word_tokenize(s)
    if len(toks) == 0:
        return False
    
    # Generate the POS tags for the words in the sentence
    tags = nltk.pos_tag(s)
    
    # Check for existence of verb
    hasVerb = reduce(lambda x,y: x or y, map(isVerb, tags))
    
    # Check for a reasonable length
    isMinLength = (len(toks) > MIN_SENTENCE_LENGTH)
    
    # Check for correct end punctuation
    wi = word_util.WordIdentity()
    hasEndPunct = wi.isEndPhrasePunc(toks[-1])
    
    # Must have all criteria to be deemed a reasonable sentence
    return hasVerb and isMinLength and hasEndPunct
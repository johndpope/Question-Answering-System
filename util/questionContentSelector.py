#!/usr/bin/python
# TODO: amend the critiria
# questionContentSelector.py
# Authored by Ryhan Hassan | rhassan@andrew.cmu.edu
# Identifies declarative sentences in source text
# that are candidates for question generation.

import re
import nltk
from util.tagUtil import *

# Use part-of-speech tagging to
# score the usefulness of a sentence.
def entity_score(sentence):
    tokens = nltk.word_tokenize(sentence)
    tokensU = map(lambda (x): x.upper, tokens)
    if (2 < len(tokens) and len(tokens) < 12):
        if ("IS" in tokensU or "WAS" in tokensU or
                "WERE" in tokensU or "BEING" in tokensU or
                "ARE" in tokensU):
            if (nltk.pos_tag([tokens[0]])[0] == "PRP"):
                return 1.0
            else:
                return 0.5

    # tagged = nltk.pos_tag(tokens)
    # entities = nltk.chunk.ne_chunk(tagged)
    score = 0
    return score

# Temporary naive approach to scoring a sentence
def naive_score(sentence):
    word_count = len(nltk.word_tokenize(sentence))
    weird = not any((c in sentence) for c in "?;:[]()"),

    features = [
        not weird,             # Avoid weird characters
        "It is" in sentence,   # Look for "It is ..."
        " is " in sentence,    # Look for "[foo] is [bar]"
        4 < word_count < 12,
        5 < word_count < 7
    ]
    return float(sum(features))/len(features)

def sentence_score(sentence):
    return 0.1*naive_score(sentence) + 0.9*entity_score(sentence)

# def qualified_sentence(s):
#     toks = nltk.word_tokenize(s)
#     tags = nltk.pos_tag(s)
#     if len(toks) == 0:
#         return False
#     # Check for existence of verb
#     hasVerb = reduce(lambda x,y: x or y, map(is_verb, tags))
#     # Check for a reasonable length
#     isMinLength = (len(toks) > MIN_SENTENCE_LENGTH)
#     # Check for correct end punctuation
#     wi = word_util.WordIdentity()
#     hasEndPunct = wi.isEndPhrasePunc(toks[-1])
#     # Must have all criteria to be deemed a reasonable sentence
#     return hasVerb and isMinLength and hasEndPunct

# GIVEN a list of sentence candidates
# RETURNS a list sorted by sentence quality score
def process(sentences):
    # sentences = filter(qualified_sentence, sentences)
    sentences = sorted(sentences, key = lambda (x): -sentence_score(x))
    return sentences




# from collections import deque;
# from copy import deepcopy;
# from util.tagUtil import *
# from util.wordUtil import WordIdentity
# import nltk;

# # Minimum number of tokens required in a sentence to turn it into a question
# MIN_SENTENCE_LENGTH = 5

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
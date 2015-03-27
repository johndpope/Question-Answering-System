#!/usr/bin/python
# TODO: amend the critiria
# questionContentSelector.py
# Authored by Ryhan Hassan | rhassan@andrew.cmu.edu
# Identifies declarative sentences in source text
# that are candidates for question generation.

import re
import nltk
from nltk.parse.stanford import StanfordParser
from nltk.tree import Tree
from util.tagUtil import *
from util.wordUtil import *



# Use part-of-speech tagging to
# score the usefulness of a sentence.
def entity_score(sentence):
    tokens = nltk.word_tokenize(sentence)
    tokensU = map(lambda (x): x.upper(), tokens)
    if (2 < len(tokens) and len(tokens) < 15):
        # print tokensU
        if ("IS" in tokensU or "WAS" in tokensU or
                "WERE" in tokensU or "BEING" in tokensU or
                "ARE" in tokensU):
            # print nltk.pos_tag([tokens[0]])[0][1]
            if (nltk.pos_tag([tokens[0]])[0][1] == "PRP"):
                return 1.0
            else:
                return 0.5

    # tagged = nltk.pos_tag(tokens)
    # entities = nltk.chunk.ne_chunk(tagged)
    score = 0
    return score

# Temporary naive approach to scoring a sentence
def strategic_score(sentence):
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

def score(sentence):
    tokens = nltk.word_tokenize(sentence)
    word_count = len(tokens)

    tokensU = map(lambda (x): x.upper(), tokens)
    tagged = nltk.pos_tag(tokens)
    weird = any((c in sentence) for c in "?;:[]()")
    
    
    if re.search(r"\b\d\d\d\d\b", sentence) == None: year_found = 0
    else: year_found = 1

    if word_count < 4:
        return 0

    if not has_verb(tagged):
        return 0

    if tokens[-1] != '.':
        return 0
    
    features = [
        year_found,
        not weird,             # Avoid weird characters
        4 < word_count < 15,
        5 < word_count < 9
    ]

    return float(sum(features))/len(features)

# english_parser = StanfordParser('StanfordCoreNLP/stanford-parser.jar', 'StanfordCoreNLP/stanford-parser-3.4.1-models.jar')
# def split_NPVP_Tree(root):
#     if len(root) == 1 and (root.label() == 'ROOT' or root.label() == 'S'):
#         return split_NPVP_Tree(root[0])
#     else:
#         if root[0].label() == 'NP' and root[1].label() == 'VP':
#             return root[0], root[1]
#         else:
#             return None, None

def has_verb(tagged):
    pnt = 0
    while pnt < len(tagged) :
        if is_verb(tagged[pnt][1]):
            return True
        pnt += 1
    return False
    
def sentence_score(sentence):
    s = score(sentence)
    # print s
    return s
    # e_s = entity_score(sentence)
    # print e_s
    # return 0.1*strategic_score(sentence) + 0.9*e_s #entity_score(sentence)

# Returns True if the string s can reasonably be described as a sentence
# The metrics we define for qualified "sentence" are:
# 1. longer or equal to minimum length
# 2. contain a verb
# 3. has end punctuation 
MIN_SENTENCE_LENGTH = 4
def qualified_sentence(s):
    print s
    toks = nltk.word_tokenize(s)
    tags = nltk.pos_tag(s)
    if len(toks) == 0:
        return False
    # Check for existence of verb
    has_verb = reduce(lambda x,y: x or y, map(is_verb, tags))
    # Check for a reasonable length
    # leq_min_length = (len(toks) >= MIN_SENTENCE_LENGTH)
    # Check for correct end punctuation
    # wi = WordIdentity()
    # has_endpunc = wi.is_endpunc(toks[-1])

    # Must have all criteria to be deemed a reasonable sentence
    return has_verb #and leq_min_length # and has_endpunc

# GIVEN a list of sentence candidates
# RETURNS a list sorted by sentence quality score
def process(sentences):
    # sentences = filter(qualified_sentence, sentences)
    scores = map(lambda (x): -sentence_score(x), sentences)
    tuples = zip(scores,sentences)
    filtered_tuples = filter(lambda (y,x): y != 0, tuples)
    sentences_sorted = [x for (y,x) in sorted(filtered_tuples)]
    # sentences = sorted(sentences, key=lambda (x): scores)
    # sentences = sorted(sentences, key = lambda (x): -sentence_score(x))
    return sentences_sorted
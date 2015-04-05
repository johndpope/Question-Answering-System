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

subconj = set(["because", "once", "when", "whenever"])

# The metrics we define for qualified "sentence" are:
# 1. longer or equal to minimum length
# 2. contain a verb
# 3. has end punctuation 
def sentence_score(sentence):
    tokens = nltk.word_tokenize(sentence)
    word_count = len(tokens)

    tokensU = map(lambda (x): x.upper(), tokens)
    tagged = nltk.pos_tag(tokens)
    weird = any((c in sentence) for c in "?;:[]()")
    
    # Search for YEAR
    if re.search(r"\b\d\d\d\d\b", sentence) == None: year_found = 0
    else: year_found = 1

    if word_count < 4:
        return 0

    if not has_verb(tagged):
        return 0

    if tokens[-1] != '.':
        return 0

    # the word "also" leads to ambiguity 
    if "also" in tokens:
        return 0
    
    has_subconj = 0
    for sc in subconj:
        if sc in sentence.lower():
            has_subconj = 1
            break

    # TODO: give score to SBAR
    features = [
        year_found,
        # ("more" in sentence)*2,     # Look for "... more ..."
        # ("less" in sentence)*2,     # Look for "... less ..."
        has_subconj*2,     # Look for "... less ..."
        not weird,                  # Avoid weird characters
        4 < word_count < 13,
        5 < word_count < 8
    ]

    return float(sum(features))/len(features)

def has_verb(tagged):
    pnt = 0
    while pnt < len(tagged) :
        if is_verb(tagged[pnt][1]):
            return True
        pnt += 1
    return False
    
# english_parser = StanfordParser('StanfordCoreNLP/stanford-parser.jar', 'StanfordCoreNLP/stanford-parser-3.4.1-models.jar')
# def split_NPVP_Tree(root):
#     if len(root) == 1 and (root.label() == 'ROOT' or root.label() == 'S'):
#         return split_NPVP_Tree(root[0])
#     else:
#         if root[0].label() == 'NP' and root[1].label() == 'VP':
#             return root[0], root[1]
#         else:
#             return None, None

# GIVEN a list of sentence candidates
# RETURNS a list sorted by sentence quality score
def process(sentences):
    scores = map(lambda (x): -sentence_score(x), sentences)
    tuples = zip(scores,sentences)
    filtered_tuples = filter(lambda (y,x): y != 0, tuples)
    sentences_sorted = [x for (y,x) in sorted(filtered_tuples)]
    return sentences_sorted
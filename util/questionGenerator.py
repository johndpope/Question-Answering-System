#!/usr/bin/python

# questionGenerator.py
# Auther: Kuang-Huei Lee | kuanghul@andrew.cmu.edu
# Transforms sentences into questions.

import re
import nltk
import random
from util.tagUtil import *
from util.wordUtil import *
from util.questionTransformer import QuestionTransformer
import util.rdrpos as rdrpos
from nltk.parse.stanford import StanfordParser
from nltk.tag.stanford import POSTagger
from nltk.tag.stanford import NERTagger
from nltk.stem.wordnet import WordNetLemmatizer


stanford_parser = StanfordParser('StanfordCoreNLP/stanford-parser.jar', 'StanfordCoreNLP/stanford-parser-3.4.1-models.jar')
stanford_postagger = POSTagger('util/stanford-postagger/models/english-bidirectional-distsim.tagger','util/stanford-postagger/stanford-postagger.jar') 

def capitalize_First_Char(sentence):
    sentence[0] = sentence[0].upper()
    return sentence

# GIVEN string sentence
# RETURNS (question string, success boolean)
def transform_IT_IS(sentence):
    if ("It is" in sentence):
        question = sentence.replace("It is", "What is")
        return (question, True)
    return (sentence, False)

# def generate_yes_no_question_from_NVN

def add_questionmark(sentence):
    if (sentence[len(sentence) - 1] == '.'):
        sentence = sentence[:len(sentence) - 1]
    return sentence + "?"

# GIVEN string representing a declarative sentence,
# RETURNS string representing a question.
def transform(sentence):

    sentence = add_questionmark(sentence)   # '.' -> '?'

    (question, success) = transform_IT_IS(sentence)
    if success: return (question, True)

    # Switch PRP and VBZ Be
    BEING = [ "IS", "ARE", "WAS", "WERE"]
    tokens = nltk.word_tokenize(sentence)
    posTag = nltk.pos_tag([tokens[0]])[0]

    add_why = 0

    #if (tokens[1].upper() in BEING and posTag == 'PRP'):
    if (len(tokens) > 1 and tokens[1].upper() in BEING):
        tokens = [tokens[1].capitalize(), tokens[0].lower()] + tokens[2:]

        if (add_why):
            tokens = ["Why", tokens[0].lower()] + tokens[1:]

        question = " ".join(tokens)
        if ("," in question):
            question = question.split(",")[0] + "?"

        return (question, True)

    if (len(tokens) > 2 and tokens[2].upper() in BEING):
        tokens = [tokens[2].capitalize(), tokens[0].lower(), tokens[1].lower()] + tokens[3:]
        #return (" ".join(tokens), True)

        if (add_why):
            tokens = ["Why", tokens[0].lower()] + tokens[1:]

        question = " ".join(tokens)
        if ("," in question):
            question = question.split(",")[0] + "?"
        return (question, True)

    if (tokens[0].upper() == "IT"):
        tokens = ["What"] + tokens[1:]
        question = " ".join(tokens)
        if ("," in question):
            question = question.split(",")[0] + "?"
        return (question, True)

    """
    tagged = nltk.pos_tag(tokens)
    entities = nltk.chunk.ne_chunk(tagged)
    (word0, tag0) = tagged[0]
    (word1, tag1) = tagged[1]
    if (tag0 == 'PRP' and tag1 =='VBZ'):
        tokens = [word1.capitalize(), word0.lower()] + tokens[2:]
        return (" ".join(tokens), True)
    """
    #print("FAIL: " + sentence)

    return (sentence, False)

def trans_Q(sentence, s_parser, s_postagger, s_NERtagger):
    qt = QuestionTransformer(sentence, s_parser, s_postagger, s_NERtagger)
    q = qt.transform_IF_TO_WHY_WILL()
    if q != None: return (q, True)
    q = qt.transform_NER_based()
    if q != None: return (q, True)
    q = qt.transform_WHEN_FROM_YEAR()
    if q != None: return (q, True)
    q = qt.transform_YES_NO_NPVP(None, None)
    if q != None: return (q, True)
    q = qt.transform_IT_IS()
    if q != None: return (q, True)
    # failed on trasforming this sentence
    return (sentence, False)

# more JJ -> less JJ
# more than -> less than
# antonyms
def hard_question_transform(token_list):
    pass
    
# GIVEN list of sentences,
# RETURNS list of questions.
def process(sentences):
    # Initialize Stanford NLP tool
    s_parser = StanfordParser('StanfordCoreNLP/stanford-parser.jar', 'StanfordCoreNLP/stanford-parser-3.4.1-models.jar')
    s_postagger = POSTagger('util/stanford-postagger/models/english-bidirectional-distsim.tagger','util/stanford-postagger/stanford-postagger.jar') 
    s_NERtagger = NERTagger('util/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz','util/stanford-ner/stanford-ner.jar')

    questions = [ ]
    for sentence in sentences:
        # print sentence
        # tags = rdrpos.pos_tag(sentence.strip())
        # print tags
        # tokens = nltk.word_tokenize(sentence)
        # print stanford_postagger.tag(tokens)
        # print stanford_parser.tag(sentence.strip())
        # (question, success) = trasform(sentence)
        (token_list, success) = trans_Q(sentence, s_parser, s_postagger, s_NERtagger)
        if (success): questions.append(' '.join(token_list))
        # TODO: antomyns, synmyms
    return questions
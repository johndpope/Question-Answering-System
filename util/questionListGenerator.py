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
pronouns_to_rule_out = set(['he','she','his','her','him','hers','this','it','its','them','themselves','himself','herself'])

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

    return (sentence, False)

# Drop sentences with pronouns
def check_pronouns(token_list):
    if any(token in pronouns_to_rule_out for token in token_list):
        return False
    else:
        return True

def transform_hard_question(q):
    if "more" in q:
        i = q.index("more")
        if q[i-1] != "once":
            q[i] = "less"
    elif "less" in q:
        i = q.index("less")
        q[i] = "more"
    return q

def generate_question(sentence, s_parser, s_postagger, s_NERtagger):

    transformer = QuestionTransformer(sentence, s_parser, s_postagger, s_NERtagger)
    q = transformer.transform_SBAR()
    if q != None:
        return (q, True)
    q = transformer.transform_IF_TO_WHY()
    if q != None:
        return (q, True)
    q = transformer.transform_IF_TO_WHY()
    if q != None:
        return (q, True)
    q = transformer.transform_NER_based()
    if q != None: 
        return (q, True)
    q = transformer.transform_YES_NO_NPVP(None, None)
    if q != None:
        q = transform_hard_question(q)
        return (q, True)
    q = transformer.transform_IT_IS()
    if q != None:
        return (q, True)

    # failed on trasforming this sentence
    return (sentence, False)

# Add question mark and captalize the question
def finalize_question(token_list):
    token_list.append('?')
    question = ' '.join(token_list)
    return question[0].upper() + question[1:]
    
# GIVEN list of sentences,
# RETURNS list of questions.
def process(sentences, num_questions):

    # Initialize Stanford NLP tool
    s_parser = StanfordParser('StanfordCoreNLP/stanford-parser.jar', 'StanfordCoreNLP/stanford-parser-3.4.1-models.jar')
    s_postagger = POSTagger('util/stanford-postagger/models/english-bidirectional-distsim.tagger','util/stanford-postagger/stanford-postagger.jar') 
    s_NERtagger = NERTagger('util/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz','util/stanford-ner/stanford-ner.jar')

    questions = []
    for sentence in sentences:
        # print sentence
        (token_list, success) = generate_question(sentence, s_parser, s_postagger, s_NERtagger)
        if (success) and check_pronouns(token_list):
            questions.append(finalize_question(token_list))
        if len(questions) >= num_questions:
            break
    return questions
#!/usr/bin/python
# 
# Usage: ./ask.py article_path num_questions
# 
from nltk.tag.stanford import POSTagger

import nltk
from article import Article
from util.nltkHelper import *
import util.questionContentSelector as selector
import util.questionListGenerator as questionListGenerator
import traceback, sys, re


if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.exit("""
            Usage: ./ask.py article_file.htm N
            article_file    HTML file containing the article HTML content
            N               Number of questions to output.
        """)

    article_filename = sys.argv[1]
    num_questions = int(sys.argv[2])

    article = Article(article_filename, 'processed')
    sentences = article.get_sentence_list(False, False, False)

    # Fetch sentence candidates that can be converted into questions.
    selected_sentences = selector.process(sentences)
    # for sent in selected_sentences:
        # print sent        
    
    # Use POS Tagging and Transformation rules to generate questions
    questions = questionListGenerator.process(selected_sentences, num_questions)

    # Select tops and print questions
    questions = questions[:num_questions]
    for question in questions:
        print question

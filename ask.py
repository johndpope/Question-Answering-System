#!/usr/bin/python
# 
# Usage: ./ask.py article_path num_questions
# 
from nltk.tag.stanford import POSTagger

import nltk
from util.article import Article
from util.nltkHelper import *
import util.questionContentSelector as selector
import util.questionGenerator as questionGenerator
import traceback, sys, re


if __name__ == "__main__":

    # the set of pronouns, used for anaphora resolution
    pronouns = set(["he", "she", "it", "its", "it's", "him", "her", "his","they",
                "their","we", "our","i","you","your","my","mine","yours","ours"])

    if len(sys.argv) != 3:
        sys.exit("""
            Usage: ./ask.py article_file.htm N
            article_file    HTML file containing the article HTML content
            N               Number of questions to output.
        """)

    # print get_synonyms("prefer")[0].examples()
    # print get_antonym()


    article_filename = sys.argv[1]
    num_questions = int(sys.argv[2])

    article = Article(article_filename)
    sentences = article.to_sentences_list()

    # Fetch sentence candidates that can be converted into questions.
    selected_sentences = selector.process(sentences)
    # for sent in selected_sentences:
    #     print sent

    # Use POS Tagging and Transformation rules to generate questions
    questions = questionGenerator.process(selected_sentences[:num_questions*2])

    # Select tops and print questions
    # questions = questions[:num_questions]
    for question in questions:
        print question

#!/usr/bin/python
# 
# Usage: ./ask.py article_file.htm N
# 

# from ask.sent_2_q import ConstructQuestion
import util.sentence_util as sentence_util
import util.nltk_helper as nltk_helper
from util.article_parser import MyHTMLParser

import nltk
import bs4
import traceback, sys, re



if __name__ == "__main__":


    # the set of pronouns, used for anaphora resolution
    pronouns = set(["he", "she", "it", "its", "it's", "him", "her", "his","they",
                "their","we", "our","i","you","your","my","mine","yours","ours"])

    resolved_articles = {}    
    
    if len(sys.argv) != 3:
        sys.exit("""
            Usage: ./ask.py article_file.htm N
            article_file    HTML file containing the article HTML content
            N               Number of questions to output.
        """)

    articleFilename = sys.argv[1]
    N = int(sys.argv[2])

    try:
        # articleFd = open(articleFilename, 'r')

        tagged_article = open(articleFilename.replace("txt", "tagged")).read()
        tagged_article = "<root>"+tagged_article+"</root>" # trick arkref into doing entire doc
        soup = bs4.BeautifulSoup(tagged_article, "html.parser").root
        for entity in soup.find_all(True):
          if entity.string != None and entity.string.strip().lower() in pronouns:
            antecedent_id = entity["entityid"].split("_")[0]
            antecedent = soup.find(mentionid=antecedent_id)
            antecedent = str(antecedent).split(">", 1)[1].split("<", 1)[0]
            #string = re.sub('<.*?>',' ',str(antecedent))
            #tok = nltk.word_tokenize(string)
            #ants = [(x,y) for x,y in nltk.pos_tag(tok) if y in {'NNP','NN'}]
            entity.string.replace_with(antecedent)
        resolved = re.sub("<.*?>", "", str(soup))
        resolved_u = resolved.decode("utf8")
        sentences = nltk.sent_tokenize(resolved_u)
        # sentenceList = nltk_helper.parseTextToSentences(resolved)
        print sentences

    except IOError:
        sys.stderr.write("Could not find article file: %s\n" % (articleFilename));

    # # Read text of the article and turn sentences into questions
    # try:

    #     # parser = MyHTMLParser()
    #     # text = articleFd.read()
    #     # parser.feed(text)
        
    #     # Retrieve the list of sentences within the article from the parser
    #     # sentenceList = parser.grabTextSentenceList()
    #     # print sentenceList
    #     # sentenceList = filter(sentence_util.isSentence, sentenceList)
        
        
    # except IOError:
    #     sys.stderr.write("An I/O error occurred while processing the article.  Details:\n")
    #     traceback.print_exc(file=sys.stderr)
    
    # finally :
        # articleFd.close()    

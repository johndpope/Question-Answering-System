import bs4
import re
import nltk
import util.nltkHelper as nltkHelper
# import subprocess

class Article(object):

    # TODO: add coref

    def __init__(self, html_filename):
        self.html_filename = html_filename
        self.content = self.parse_html()

    def parse_html(self):
        try:
            article_fd = open(self.html_filename).read()
            article_fd = "<root>"+article_fd+"</root>" # trick arkref into doing entire doc
            soup = bs4.BeautifulSoup(article_fd, "html.parser").root
            resolved = re.sub("<.*?>", "", str(soup))
        except:
            resolved = open(self.html_filename).read()
        resolved_u = resolved.decode("utf8")
        return resolved_u

    def to_sentences_list(self):
        sentence_list = nltk_helper.parseTextToSentences(self.content)
        return sentence_list
    
    # def parse_html_coref(self):
    #     pronouns = set(["he", "she", "it", "its", "it's", "him", "her", "his","they",
    #             "their","we", "our","i","you","your","my","mine","yours","ours"])
    #     path_to_article = self.html_filename
    #     original_path = self.html_filename
    #     # try:
    #     fh = open("NUL","w")
    #     subprocess.call(["./arkref.sh", "-input", path_to_article], stdout = fh, stderr = fh)
    #     fh.close()

    #     tagged_article = open(path_to_article.replace("txt", "tagged")).read()
    #     print path_to_article.replace("txt", "tagged")
    #     tagged_article = "<root>"+tagged_article+"</root>" # trick arkref into doing entire doc
    #     soup = bs4.BeautifulSoup(tagged_article, "html.parser").root
    #     for entity in soup.find_all(True):
    #         if entity.string != None and entity.string.strip().lower() in pronouns:
    #             antecedent_id = entity["entityid"].split("_")[0]
    #             antecedent = soup.find(mentionid=antecedent_id)
    #             antecedent = str(antecedent).split(">", 1)[1].split("<", 1)[0]
    #             entity.string.replace_with(antecedent)
    #     resolved = re.sub("<.*?>", "", str(soup))
    #     # except:
    #         # pass
    #         # resolved = open(original_path).read()
    #     resolved_u = resolved.decode("utf8")
    #     return resolved_u

    # def to_sentences_list_coref(self):
    #     sentence_list_coref = nltk_helper.parseTextToSentences(self.content_coref)
    #     return sentence_list_coref
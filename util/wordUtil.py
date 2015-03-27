import re, nltk;

# set definitions here
# allows for quick change and quick intersection / union, subtraction of sets
# be CAREFUL of abbreviations (converts to lower for check);
timewords = set(['today','tomorrow','yesterday'])
q_words = set(['who','what','where','when','why','did','do','does','is','was','how'])
endpunc = set(['!', ',','.',';','?'])
be_verb = set(['is','am','are','was','were'])


def is_be_verb(word):
    return word.lower() in be_verb

def is_endpunc(word):
    return word.lower() in endpunc

def is_question_word(word):
    return word.lower() in q_words

# def is_name_pre(self, word):
#     return word.lower() in namePre

# determinds if a word is proper noun based on the tag "NNP" or the capitalization
def is_prop_n(word, tag):
    return tag == "NNP" or word[0].isupper()

# Test
if __name__ == "__main__":
    print is_be_verb('is') 
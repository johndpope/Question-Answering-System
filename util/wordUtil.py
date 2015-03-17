import re, nltk;

# set definitions here
# allows for quick change and quick intersection / union, subtraction of sets
# be CAREFUL of abbreviations (converts to lower for check);
timewords = set(['today','tomorrow','yesterday']);
q_words = set(['who','what','where','when','why','did','do','does','is','was','how']);
link_verb = set(['is', 'am', 'are','was']);
is_endpunc = set(['!', ',','.',';','?']);
sub_pronouns = set(['he','she','we','they','i']);
obj_pronouns = set(['her','him','me','us','them']);
pos_pronouns = set(['their','his','her','our','my']);
being_verb = set(['is','are','was','were']);


class WordIdentity(object):

    def is_being_verb(self,word):
        return word.lower() in beingV;

    def is_endpunc(self,word):
        return word.lower() in endPhrasePunc;

    def is_month(self,word):
        return word.lower() in months;

    def is_day_of_week(self, word):
        return word.lower() in days;

    def is_time_word(self, word):
        return word.lower() in timewords;
        
    def is_question_word(self,word):
        return word.lower() in qWords;

    def is_name_pre(self, word):
        return word.lower() in namePre;

    def is_link_Verb(self,word):
        return word.lower() in linkVerb;

    # determinds if a word is proper noun based on the tag "NNP" or the capitalization
    def is_prop_n(self,word, tag):
        return tag == "NNP" or word[0].isupper();
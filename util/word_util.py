import re, nltk;

# set definitions here
# allows for quick change and quick intersection / union, subtraction of sets
# be CAREFUL of abbreviations (converts to lower for check);
timewords = set(['today','tomorrow','yesterday']);
qWords = set(['who','what','where','when','why','did','do','does','is','was','how']);
linkVerb = set(['is', 'am', 'are','was']);
endPhrasePunc = set(['!', ',','.',';','?']);
subPronouns = set(['he','she','we','they','i']);
objPronouns = set(['her','him','me','us','them']);
posPronouns = set(['their','his','her','our','my']);
beingV = set(['is','are','was','were']);


class WordIdentity(object):

    def isBeingVerb(self,word):
        return word.lower() in beingV;

    def isEndPhrasePunc(self,word):
        return word.lower() in endPhrasePunc;

    def isMonth(self,word):
        return word.lower() in months;

    def isDayOfWeek(self, word):
        return word.lower() in days;

    def isTimeWord(self, word):
        return word.lower() in timewords;
        
    def isQuestionWord(self,word):
        return word.lower() in qWords;

    def isNamePre(self, word):
        return word.lower() in namePre;

    def isLinkVerb(self,word):
        return word.lower() in linkVerb;

    # determinds if a word is proper noun based on the tag "NNP" or the capitalization
    def isPropN(self,word, tag):
        return tag == "NNP" or word[0].isupper();
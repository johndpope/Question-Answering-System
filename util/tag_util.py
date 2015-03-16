import re, nltk;

def isVerb(tag):
    return (tag[:1] == 'V')

def isMd(tag):
    return (tag == 'MD')

def isNoun(tag):
    return (tag[:1] == 'N')

def isAdj(tag):
    return (tag[:2] == "JJ")

def isNum(tag):
    return (tag[:2] == "CD")

def isPropN(tag):
    return (tag == "NNP");

def isSyn(tag):
    return (tag == "SYN")

def isCustom(tag):
    return (tag == "CST")

def isHighPriority(tag):
    return (tag == "HGH")
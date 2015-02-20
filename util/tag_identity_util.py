import re, nltk;

def is_verb(tag):
    return (tag[:1] == 'V')

def is_md(tag):
    return (tag == 'MD')

def is_noun(tag):
    return (tag[:1] == 'N')

def is_adj(tag):
    return (tag[:2] == "JJ")

def is_num(tag):
    return (tag[:2] == "CD")

def is_propN(tag):
    return (tag == "NNP");

def is_syn(tag):
    return (tag == "SYN")

def is_custom(tag):
    return (tag == "CST")

def is_high_priority(tag):
    return (tag == "HGH")
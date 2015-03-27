import nltk, os, sys, re
from nltk.parse.stanford import StanfordParser
from nltk.tag.stanford import POSTagger
from nltk.tag.stanford import NERTagger
import util.rdrpos as rdrpos
from nltk.tree import Tree
from nltk.stem.wordnet import WordNetLemmatizer
from util.tagUtil import *
from util.wordUtil import *
from util.identityUtil import *

class QuestionTransformer(object):

    def __init__(self, sentence, s_parser, s_postagger, s_NERtagger):

        # Initialize Stanford NLP tool
        self.s_parser = s_parser
        self.s_postagger = s_postagger
        self.s_NERtagger = s_NERtagger

        self.sentence = sentence
        # Tokenization
        self.tokens = nltk.word_tokenize(sentence.strip())
        # build POS.tags from RDR tagger (much faster than Stanford tagger)
        self.tags = rdrpos.pos_tag(sentence.strip())
        # build NER tags
        # self.ner_tags = s_NERtagger.tag(self.tokens)
        self.ner_tags = None

        # check if capitaliaztion is necessary (First word NNP)
        if self.tags[0] != 'NNP':
            self.tokens[0] = self.tokens[0].lower()

        # remove end puncuation
        self.tokens, self.tags = self.remove_endpunc(self.tokens, self.tags)

        # length of sentence
        self.sent_length = len(self.tokens)

    # remove_endpunc - remove end punction from the given token string
    def remove_endpunc(self,tokens,tags):
        if is_endpunc(tokens[-1]):
            x = tokens.pop(-1)
            y = tags.pop(-1)
        return tokens,tags


    """
    No capitaliaztion
    Critiria:
        1. IF -> WHY Question
        2. When ?? (British surrender on 15 February 1942)
            In 1658... As of ... 
        3. Where ?
        4. Who ?
        5. YESNO Question
        3. 

    """
    """
    VB  Verb, base form
    VBD Verb, past tense
    VBG Verb, gerund or present participle
    VBN Verb, past participle
    VBP Verb, non-3rd person singular present
    VBZ Verb, 3rd person singular present
    MD model auxiliary
    have has had
    beingVerb
    How to prune?
    # cases to replace:
#   dates -> when
#   if -> why question with the if section as the clause
#   noun / proper noun / pronoun replacement
#   names / proper nouns
# In 2009, 

wordNet

    """

    """
    pruning
    """

    # Pattern: If [clause], [S] -> Why will [S] / Why MD [S]?
    # MD = should/may/could ...
    # If success, output question string
    # If fail, output None
    def transform_IF_TO_WHY_WILL(self):
        tags = self.tags
        tokens = self.tokens

        if tokens[0] != "if":
            return None

        # Avoid personal pronoun
        if "PRP" in tags:
            return None

        # check for ","
        if "," not in set(tags):
            return None
        # split on first comma (associated with "if") 
        idx = tags.index(",");
        if idx < (len(tags)-1):
            S_tokens = tokens[idx+1:]
            S_tags = tags[idx+1:]
            
            # # find the first verb modifier to be used in question
            # subset = self.transform_MD(S_tags, S_tokens)
            # if subset != None:
            #     return ["why"] + subset
            
            # if MD is not in S, use general word "will"
            subset = self.transform_YES_NO_NPVP(S_tags, S_tokens)
            if subset != None:
                return ["why"] + subset
        return None
    

    # In [year], [S]. -> WHEN transformed[S]?
    def transform_WHEN_FROM_YEAR(self):
        tags = self.tags
        tokens = self.tokens
        if len(tokens) > 3:
            if tokens[0] == "in" and re.match(r"\b\d\d\d\d\b", tokens[1]) and tokens[2] == ",":
                S_tokens = tokens[3:]
                S_tags = tags[3:]
                subset = self.transform_YES_NO_NPVP(S_tags, S_tokens)
                if subset != None:
                    return ["when"] + subset
            elif tokens[0] == "since" and re.match(r"\b\d\d\d\d\b", tokens[1]) and tokens[2] == ",":
                S_tokens = tokens[3:]
                S_tags = tags[3:]
                subset = self.transform_YES_NO_NPVP(S_tags, S_tokens)
                if subset != None:
                    return ["since","when"] + subset
            elif tokens[0] == "as" and tokens[1] == "of" and re.match(r"\b\d\d\d\d\b", tokens[2]) and tokens[3] == ",":
                S_tokens = tokens[3:]
                S_tags = tags[3:]
                subset = self.transform_YES_NO_NPVP(S_tags, S_tokens)
                if subset != None:
                    return ["since","when"] + subset
        return None

    # Test
    def transform_NER_based(self):
        tags = self.tags
        tokens = self.tokens
        for i, tag in enumerate(tags):
            if tag == "NNP" and i+1 < len(tags) and is_verb(tags[i+1]):
                if self.ner_tags == None: 
                    self.ner_tags = self.s_NERtagger.tag(self.tokens)
                # WHO question
                if self.ner_tags[i] == "PERSON":
                    return ["who"] + tokens[i+1:]
        return None



    # create WHERE question for location
    # by using Stanford NER
    def transform_WHERE():
        pass

    # create WHO question
    # by using Stanford NER
    # Looing for ... [PERSON]+[VBP/VBZ/VBD/MD] ...
    # def transform_WHO(self):
    #     tags = self.tags
    #     ner_tags = self.ner_tags
    #     tokens = self.tokens
    #     targets = ['MD','VBP','VBD','VBZ']
    #     if tags == None: tags = self.tags
    #     if tokens == None: tokens = self.tokens
    #     if "," in set(tags):
    #         return None
    #     for i in xrange(0, len(ner_tags)-1):            
    #         if i < ner_tags[i] == "PERSON" and tags[i+1] in targets:
    #             return ['who'] + tokens[i+1:]
    #     return None

    # create WHAT question
    # by using Stanford NER

    def transform_WHAT():
        pass


    def transform_YES_NO_NPNP(self):
        pass

    # create simple yes / no questions from a sentence
    # by siwtching the placement of the subject and the being verb
    def transform_YES_NO_NPVP(self, tags, tokens):
        if tags == None: tags = self.tags
        if tokens == None: tokens = self.tokens
        
        # Avoid personal pronoun
        if "PRP" in tags:
            return None

        # Find the first beverb
        for i, tag in enumerate(tags):

            # Avoid end punctuation
            if is_endpunc(tag):
                return None

            # found "Have" "Has" "had"
            if i+1 < len(tokens) and tokens[i] in ["have","has","had"] and is_verb(tags[i+1]):
                return self.transform_HAVE(tags, tokens, i)

            # found a model verb
            if is_md(tag):
                return self.transform_MD(tags, tokens)

            # found a verb
            if is_verb(tag):
                q_token_sets = self.transform_VERB(tags, tokens, i)
                if q_token_sets != None:
                    return q_token_sets
        return None

    def transform_HAVE(self, tags, tokens, i):
        subset_before_verb = tokens[:i]
        if i < len(tags)-1: subset_after_verb = tokens[i+1:]
        return [tokens[i]] + subset_before_verb + subset_after_verb

    def transform_VERB(self, tags, tokens, i):
        # found a beverb
        if is_be_verb(tokens[i]):
            subset_before_verb = tokens[:i]
            if i < len(tags)-1: subset_after_verb = tokens[i+1:]
            return [tokens[i]] + subset_before_verb + subset_after_verb
        # found a doverb
        else:
            if tags[i] == 'VBP':
                prefix = 'do'
            elif tags[i] == 'VBD':
                prefix = 'did'
            elif tags[i] == 'VBZ':
                prefix = 'does'
            else:
                return None
            lemmatized_verb = WordNetLemmatizer().lemmatize(tokens[i],'v')
            subset_before_verb = tokens[:i]
            if i < len(tags)-1:
                subset_after_verb = tokens[i+1:]
                return [prefix] + subset_before_verb + [lemmatized_verb] + subset_after_verb
            else:
                return [prefix] + subset_before_verb + [lemmatized_verb]

    def transform_MD(self, tags, tokens):
        if tags == None: tags = self.tags
        if tokens == None: tokens = self.tokens

        if "MD" in set(tags):
            MD_idx = tags.index("MD")
            MD_verb = tokens[MD_idx]
            subset_before_MD = tokens[:MD_idx]
            if MD_idx < len(tags)-1: subset_after_MD = tokens[MD_idx+1:]
            return [MD_verb] + subset_before_MD + subset_after_MD
        else:
            return None

    # GIVEN string sentence
    # RETURNS (question string, success boolean)
    def transform_IT_IS(self):
        tokens = self.tokens
        if self.tokens[0] == "it" and self.tokens[1] == "is":
            return ["what"] + tokens[1:]
        return None
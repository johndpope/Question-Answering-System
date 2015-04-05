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

# TODO: But ..., ..., detect SBAR get rid of But
# Because, Because of

class QuestionTransformer(object):

    def __init__(self, sentence, s_parser, s_postagger, s_NERtagger):

        # Initialize Stanford NLP tool
        self.s_parser = s_parser
        self.s_postagger = s_postagger
        self.s_NERtagger = s_NERtagger

        # Copy sentence
        self.sentence = sentence
        # Tokenization
        self.tokens = nltk.word_tokenize(sentence.strip())
        # build POS.tags from RDR tagger (much faster than Stanford tagger)
        self.tags = rdrpos.pos_tag(sentence.strip())
        # Initialize NER tags
        self.ner_tags = None
        # Initialize parse tree
        self.tree = None

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
    #   noun / proper noun / pronoun replacement
    #   names / proper nouns
    """

    # Pattern: If [clause], [S] -> Why will [S] / Why MD [S]?
    # MD = should/may/could ...
    # If success, output question string
    # If fail, output None
    def transform_IF_TO_WHY(self):
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
            subset = self.transform_YES_NO_NPVP(S_tags, S_tokens)
            if subset != None:
                return ["why"] + subset
        return None
    

    # In [year], [S]. -> WHEN transformed[S]?
    def transform_WHEN_FROM_YEAR(self):
        tags = self.tags
        tokens = self.tokens
        if len(tokens) > 3 and re.search(r"\b\d\d\d\d\b", self.sentence):
            # from the begining of sentence
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

            for i in xrange(3, len(tokens)):
                subset = None
                if re.match(r"\b\d\d\d\d\b", tokens[i]):
                    if tokens[i-1] == "in":
                        S_tokens = tokens[:i-1]
                        S_tags = tags[:i-1]
                        subset = self.transform_YES_NO_NPVP(S_tags, S_tokens)
                    elif is_month(tokens[i-1]) and tokens[i-2] == "in":
                        S_tokens = tokens[:i-2]
                        S_tags = tags[:i-2]
                        subset = self.transform_YES_NO_NPVP(S_tags, S_tokens)
                    elif is_month(tokens[i-1]) and re.match(r"\d+", tokens[i-2]) and tokens[i-3] == "on":
                        S_tokens = tokens[:i-3]
                        S_tags = tags[:i-3]
                        subset = self.transform_YES_NO_NPVP(S_tags, S_tokens)
                    if subset != None and "," not in subset and "and" not in subset:
                        return ["when"] + subset
        return None

    # create WHERE question for location
    # by using Stanford NER
    def transform_NER_based(self):
        tags = self.tags
        # print tags
        tokens = self.tokens
        for i, tag in enumerate(tags):

            # Generate WHO based quesiton
            if tag == "NNP" and i+1 < len(tags) and (is_verb(tags[i+1]) or is_md(tags[i+1])):
                if self.ner_tags == None: 
                    self.ner_tags = self.s_NERtagger.tag(self.tokens)
                # print self.ner_tags[i][1]
                if self.ner_tags[i][1] == "PERSON":
                    return ["who"] + tokens[i+1:]
        return None

    # e.g. The neck graft allows the original scroll to be kept with a Baroque violin when bringing its neck into conformance with modern standards.
    # Use Stanford parse tree "SBAR -> WHADVP S" or "SBAR -> IN S"
    # SBAR list: http://www.chompchomp.com/terms/subordinateconjunction.htm
    def transform_SBAR(self):
        

        subconj = set(["because", "once", "when", "whenever"])
        when_group = set(["once", "when", "whenever"])
        why_group = set(["because"])
        # Check if the sentence has any subconj we want
        has_subconj = False
        for token in self.tokens:
            if token in subconj:
                has_subconj = True
                break

        if has_subconj == False:
            return None

        # Build parse tree
        if self.tree == None:
            trees = self.s_parser.parse_sents([self.tokens])
            self.tree = trees[0]
            # self.tree.draw()

        # don't want FRAG for the time being
        if self.tree[0].label() == "FRAG":
            return None

        # DFS SBAR Tree
        SBAR_tree = self.parsetree_DFS(self.tree, "SBAR")
        if SBAR_tree == None:
            return None
        
        # print SBAR_tree
        
        SBAR_tokens = SBAR_tree.leaves()
        rest_tokens = None
        rest_tags = None

        if len(SBAR_tokens) == self.sent_length:
            return None
        
        # Check for alignment and position of SBAR in the sentence
        SBAR_begin = self.tokens.index(SBAR_tokens[0])
        SBAR_end = SBAR_begin + len(SBAR_tokens) - 1


        if len(SBAR_tokens) < 3:
            return None
            
        for i in xrange(0, 3):
            if self.tokens[SBAR_begin+i] != SBAR_tokens[i]:
                return None


        # print SBAR_tokens
        # If SBAR at the begining of sentence
        if SBAR_begin == 0:
            rest_tokens = self.tokens[SBAR_end+1:]
            rest_tags = self.tags[SBAR_end+1:]
            # Remove comma after SBAR
            if rest_tokens[0] == ",":
                rest_tokens.pop(0)
                rest_tags.pop(0)
        elif SBAR_end == self.sent_length - 1:
            rest_tokens = self.tokens[:SBAR_begin]
            rest_tags = self.tags[:SBAR_begin]
            
            # Remove comma before SBAR
            if rest_tokens[-1] == ",":
                rest_tokens.pop(-1)
                rest_tags.pop(-1)
        else:
            return None

        if SBAR_tokens[0] in when_group:
            subset = self.transform_YES_NO_NPVP(rest_tags, rest_tokens)
            if subset != None:
                return ["when"] + subset
        
        elif SBAR_tokens[0] in why_group:
            subset = self.transform_YES_NO_NPVP(rest_tags, rest_tokens)
            if subset != None:
                return ["why"] + subset
        

        return None
        

    def parsetree_DFS(self, tree, target_tag):

        if isinstance(tree, unicode):
            return None

        if (tree.label() == target_tag):
            return tree

        # print len(tree)
        for subtree in tree:
            res = None
            res = self.parsetree_DFS(subtree, target_tag)
            if res != None:
                return res

        return None
    
    # def transform_WHERE():
    #     pass

    # def transform_WHAT():
    #     pass

    def transform_YES_NO_NPNP(self):
        pass

    # create simple yes / no questions from a sentence
    # by siwtching the placement of the subject and the being verb
    def transform_YES_NO_NPVP(self, tags, tokens):

        if tags == None: tags = self.tags
        if tokens == None: tokens = self.tokens
        
        target_verb_set = set(['VBP', 'VB', 'VBD', 'VBZ'])

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
            if tag in target_verb_set:
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
            if tags[i] == 'VBP' or 'VB':
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
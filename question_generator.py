import nltk, os, sys
from nltk.parse.stanford import StanfordParser
from nltk.tree import Tree
from nltk.stem.wordnet import WordNetLemmatizer
from util.tag_util import *
from util.word_util import WordIdentity

class QuestionGenerator(object):

    def __init__(self):
        self.english_parser = StanfordParser('StanfordCoreNLP/stanford-parser.jar', 'StanfordCoreNLP/stanford-parser-3.4.1-models.jar')
        self.wordID = WordIdentity()

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
    """

    """
    pruning
    """

    def generateYesNoQuestionNVN(self, sent):
        tree = self.english_parser.raw_parse_sents((sent, ))
        root = tree[0]
        NPTree, VPTree = self.splitNVNTree(root)
        rephrasedNPVPQ = self.rephraseQuestion(NPTree, VPTree)
        return rephrasedNPVPQ

    def rephraseQuestion(self, NPTree, VPTree):
        VP_POS = VPTree.pos()    
        VPLeaves = VPTree.leaves()
        NPLeaves = NPTree.leaves()
        VPEnd = 0
        while is_verb(VP_POS[VPEnd][1]):
            VPEnd = VPEnd + 1
        if self.wordID.isBeingVerb(VP_POS[0][0]) or VP_POS[0][1] == 'MD':
            prefix = VP_POS[0][0]
            NP = ' '.join(NPLeaves)
            VP = ' '.join(VPLeaves[1:])
            return prefix+' '+NP+' '+VP
        elif VPEnd == 1:
            if VP_POS[0][1] == r'VBP*\b':
                prefix = 'do'
            elif VP_POS[0][1] == 'VBD':
                prefix = 'did'
            elif VP_POS[0][1] == 'VBZ':
                prefix = 'does'
            NP = ' '.join(NPLeaves)
            VP1 = WordNetLemmatizer().lemmatize(VPLeaves[0],'v')
            VP2 = ' '.join(VPLeaves[1:])
            return prefix+' '+NP+' '+VP1+' '+VP2
        elif VPEnd > 1:
            prefix = VP_POS[0][0]
            NP = ' '.join(NPLeaves)
            VP = ' '.join(VPLeaves[1:])
            return prefix+' '+NP+' '+VP
        else:
            return "Not yet implement"

    def splitNVNTree(self, root):
        if len(root) == 1 and (root.label() == 'ROOT' or root.label() == 'S'):
            return self.splitNVNTree(root[0])
        else:
            if root[0].label() == 'NP' and root[1].label() == 'VP':
                return root[0], root[1]
            else:
                return None, None

    def getleftMostVBLabel(self, root):
        if root.label() == 'VP':
            return self.getFirstVBLabel(root[0])
        else:
            return root.label()

    def testAsking(self):
        # q1 = "it is the country's principal political, cultural, commercial, industrial, and transportation centre, sometimes described as the primate city of Hungary"
        q1 = "the cat is sleeping"
        print 'question:',  q1
        print 'answer:', self.generateYesNoQuestionNVN(q1)

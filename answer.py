import sys
import nltk
import codecs
import numpy, math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet as wn

"""
In this version, no coreference resolution were included. This seems to be
OK for simple question answering, but coreference resolution is definitely
needed in answering medium and hard questions.
"""

def steming(sentences):
	"""	
		Input:  a list of sentenses
		Output: a dict of sentenses with tokens stemed,
				key = stemed sentence, value = original sentence
	"""
	porter = nltk.PorterStemmer()
	#lancaster = nltk.LancasterStemmer()
	stemedSentences = dict()
	for sentence in sentences:
		#print "Processing sentence: ", sentence
		tokens = nltk.word_tokenize(sentence)
		stemedTokens = [porter.stem(t) for t in tokens]
		# stemedSentences[sentence]=' '.join(stemedTokens)
		stemedSentences[' '.join(stemedTokens)]=sentence
	return stemedSentences

def tfidf(sentences):
	"""
	Input a dict of sentences, return the tfidf matrix
	"""
	sentences = sentences.keys()
	tfidf_vectorizer = TfidfVectorizer()
	tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)
	return tfidf_vectorizer, tfidf_matrix

def tfidfSearch(tfidf_vectorizer, tfidf_matrix, sentences, query):
	sentences = sentences.keys()
	response = tfidf_vectorizer.transform([query])
	similarities = cosine_similarity(response, tfidf_matrix).flatten()
	sortedSimilarity = numpy.argsort(similarities)[::-1]
	return sentences[sortedSimilarity[0]]

def isTooShort(line):
	tokens = nltk.word_tokenize(line)
	if len(tokens) < 5:
		return True
	return False

def readSentences(infile):
	sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
	sentences = []
	for line in infile:
		if line.strip() and (not isTooShort(line)):
			sentences += sent_tokenizer.tokenize(line)
	return sentences

def getAntonyms(s1):
	tokens = nltk.word_tokenize(s1)
	tags = nltk.pos_tag(tokens)
	antonyms = dict()
	porter = nltk.PorterStemmer()
	for (w,t) in tags:
		if t in['JJ','RB']:
			# print w,':',t,"\n"
			for i in wn.synsets(w):
				if i.pos() in ['a','s']:
					for j in i.lemmas():
						if j.antonyms():
							stemedAntonym = porter.stem(j.antonyms()[0].name())
							antonyms[stemedAntonym]=1
	# printHash(antonyms)
	return antonyms

def haveAntonyms(antonyms,s2):
	# antonyms = getAntonyms(s1)
	stemedS2 = steming([s2]).keys()[0]
	tokens = nltk.word_tokenize(stemedS2)
	for w in tokens:
		if w in antonyms:
			return True
	return False

def answerSimple(targetSentence, query, negWords):
	"""
	Improved: look up for antonym in target and query sentence
	"""
	negInTarget = 0
	negInQuery = 0
	for token in nltk.word_tokenize(targetSentence):
		if token in negWords:
			negInTarget += 1
	for token in nltk.word_tokenize(query):
		if token in negWords:
			negInQuery += 1
	antonyms = getAntonyms(query)
	if negInQuery != negInTarget:
		if haveAntonyms(antonyms,targetSentence):
			return 'Yes.'
		else:
			return 'No.'
	else:
		if haveAntonyms(antonyms,targetSentence):
			return 'No.'
		else:
			return 'Yes.'

# def answerSimple(targetSentence, query, negWords):
# 	"""
# 	To improve:
# 		look up for antonym in target and query sentence?
# 	"""
# 	negInTarget = 0
# 	negInQuery = 0
# 	for token in nltk.word_tokenize(targetSentence):
# 		if token in negWords:
# 			negInTarget += 1
# 	for token in nltk.word_tokenize(query):
# 		if token in negWords:
# 			negInQuery += 1
# 	if negInQuery != negInTarget:
# 		return 'No.'
# 	return 'Yes.'

def isSimpleQuest(question):
	i = question.find(' ')

	if 	question[0:2].lower()=='wh' \
		or question[0:3].lower()=='how' \
		or question[(i+1):(i+3)].lower()=='wh':
		return False
	return True

def printHash(myHash):
	for key in myHash.keys():
		print key,": ",myHash[key]

def main():
	if len(sys.argv) < 3:
		print 'Usage: python answer.py article.txt questions.txt\n'
		sys.exit(2)
	article = sys.argv[1]
	quests = sys.argv[2]

	print "Reading input file and split into sentences... "
	infile = codecs.open(article,encoding='utf-8')
	sentences = readSentences(infile)
	infile.close()

	print "Steming the tokens... "
	stemedSentences = steming(sentences)

	print "Building TF-IDF matrix..."
	(tfidf_vectorizer, tfidf_matrix) = tfidf(stemedSentences)

	print "Reading in Questions..."
	quesfile = codecs.open(quests,encoding='utf-8')
	questions = readSentences(quesfile)
	quesfile.close()

	print "Steming the questions..."
	stemedQuestions = steming(questions)

	print "TFIDF searching... "
	negWords = {'no':1, 'not':1, 'never':1, 'none':1, 'neither':1, 'nothing':1, 'n\'t':1}
	for q in stemedQuestions.keys():
		print "\nQuestion:\t", stemedQuestions[q].strip()
		ansSentence = tfidfSearch(tfidf_vectorizer, tfidf_matrix, stemedSentences, q)
		if isSimpleQuest(stemedQuestions[q]):
			print "Related sentence:\t", stemedSentences[ansSentence]
			print "Answer:\t\t", answerSimple(stemedSentences[ansSentence],stemedQuestions[q],negWords)
		else:
			print "Answer:\t\t",stemedSentences[ansSentence]
	
	

if __name__ == '__main__':
	main()
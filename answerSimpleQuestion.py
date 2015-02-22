import nltk
import codecs
import numpy, math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

"""
In this version, no coreference resolution were included. This seems to be
OK for simple question answering, but coreference resolution is definitely
needed in answering medium and hard questions.
"""

def steming(sentences):
	"""	
	Input: a list of sentenses
		Output: a list of sentenses with tokens stemed
	"""
	porter = nltk.PorterStemmer()
	#lancaster = nltk.LancasterStemmer()
	stemedSentences = []
	for sentence in sentences:
		#print "Processing sentence: ", sentence
		tokens = nltk.word_tokenize(sentence)
		stemedTokens = [porter.stem(t) for t in tokens]
		stemedSentences.append(' '.join(stemedTokens))
		#print "stemedSentences", ' '.join(stemedTokens)
	return stemedSentences

def tfidf(sentences):
	"""
	Input a list of sentences, return the tfidf matrix
	"""
	tfidf_vectorizer = TfidfVectorizer()
	tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)
	return tfidf_vectorizer, tfidf_matrix

def tfidfSearch(tfidf_vectorizer, tfidf_matrix, sentences, query):
	response = tfidf_vectorizer.transform([query])
	similarities = cosine_similarity(response, tfidf_matrix).flatten()
	sortedSimilarity = numpy.argsort(similarities)[::-1]
	return sentences[sortedSimilarity[0]]

def readSentences(infile):
	sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
	sentences = []
	for line in infile:
		if line.strip():
			sentences += sent_tokenizer.tokenize(line)
	return sentences

def answerSimple(targetSentence, query, negWords):
	"""
	To improve:
		look up for antonym in target and query sentence?
	"""
	negInTarget = 0
	negInQuery = 0
	for token in nltk.word_tokenize(targetSentence):
		if token in negWords:
			negInTarget += 1
	for token in nltk.word_tokenize(query):
		if token in negWords:
			negInQuery += 1
	if negInQuery != negInTarget:
		return 'No.'
	return 'Yes.'


def main():
	print "Reading input file and split into sentences... "
	infileName = '../data/set4-1.txt'
	infile = codecs.open(infileName,encoding='utf-8')
	sentences = readSentences(infile)
	infile.close()

	print "Steming the tokens... "
	stemedSentences = steming(sentences)

	print "TFIDF searching... "
	query = 'Were wire-wound strings invented in Bologna?'
	print "\nQuestion: ", query
	query = steming([query])[0]
	(tfidf_vectorizer, tfidf_matrix) = tfidf(stemedSentences)
	ansSentence = tfidfSearch(tfidf_vectorizer, tfidf_matrix, stemedSentences, query)
	print "\nRelated sentence: ", ansSentence

	### Generate answer to simple question
	negWords = {'no':1, 'not':1, 'never':1, 'none':1, 'neither':1, 'nothing':1, 'n\'t':1}
	print "\nAnswer: ", answerSimple(ansSentence,query, negWords)



if __name__ == '__main__':
	main()
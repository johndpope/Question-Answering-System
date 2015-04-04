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
		Input:  a list of cleaned sentences (i.e. stop words removed)
		Output: a list of sentenses with tokens stemed,
	"""
	porter = nltk.PorterStemmer()
	#lancaster = nltk.LancasterStemmer()
	# stemedSentences = dict()
	stemedSentences = []
	for i in range(0,len(sentences)):
		#print "Processing sentence: ", sentence
		tokens = nltk.word_tokenize(sentences[i])
		stemedTokens = [porter.stem(t) for t in tokens]
		# stemedSentences[sentence]=' '.join(stemedTokens)
		# stemedSentences[' '.join(stemedTokens)]=org[i]
		stemedSentences += [' '.join(stemedTokens)]
	return stemedSentences


def tfidf(sentences):
	"""
	Input a list of sentences, return the tfidf matrix
	"""
	# sentences = sentences.keys()
	tfidf_vectorizer = TfidfVectorizer()
	tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)
	return tfidf_vectorizer, tfidf_matrix

def tfidfSearch(tfidf_vectorizer, tfidf_matrix, sentences, query):
	# sentences = sentences.keys()
	response = tfidf_vectorizer.transform([query])
	similarities = cosine_similarity(response, tfidf_matrix).flatten()
	sortedSimilarity = numpy.argsort(similarities)[::-1]
	# return sentences[sortedSimilarity[0]]
	return sortedSimilarity[0] # the index of the sentence with largest similarity

def isTooShort(line):
	tokens = nltk.word_tokenize(line)
	if len(tokens) < 5:
		return True
	return False

def readSentences(infile):
	sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
	sentences = []
	for line in infile:
		# print line
		if (line.strip() and (not isTooShort(line))):
			single_sentences = sent_tokenizer.tokenize(line)
			for k in single_sentences:
				if ( k[-1] in ['.','!',','] ):
					sentences += [k]
	return sentences

def readQuestion(infile):
	sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
	sentences = []
	for line in infile:
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
	stemedS2 = steming([s2])[0]
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

WHwords = ['what','which','when','where','why','how','whom','who',' or ']
def isSimpleQuest(question):
	for k in WHwords:
		if k in question.lower():
			return False
	return True

def printHash(myHash):
	for key in myHash.keys():
		print key,": ",myHash[key]

def removeStopWords(sentences,stopWords):
	"""Input: a list of sentences & a dict of stop words"""
	cleanSentences = []
	for sen in sentences:
		tokens = nltk.word_tokenize(sen)
		for i in range(0,len(tokens)):
			if tokens[i].lower() in stopWords:
				tokens[i] = ''
		cleanSentences += [' '.join(tokens).strip()]
	return cleanSentences

def main():
	if len(sys.argv) < 3:
		print 'Usage: python answer.py article.txt questions.txt\n'
		sys.exit(2)
	article = sys.argv[1]
	quests = sys.argv[2]

	print >> sys.stderr, "Reading input file and split into sentences... "
	infile = codecs.open(article,encoding='utf-8')
	sentences = readSentences(infile) # a list of original sentences
	infile.close()

	print >> sys.stderr, "Remove stop words before stemming and TF-IDF..."
	stopFilePath = "./Misc/stopword.txt"
	stopFile = open(stopFilePath,'r')
	stopWords = dict()
	for word in stopFile:
		stopWords[word.strip()] = 1
	stopFile.close()
	cleanSentences = removeStopWords(sentences,stopWords) # a list of stop-free sentences
	# print cleanSentences

	print >> sys.stderr, "Steming the tokens... "
	stemedSentences = steming(cleanSentences) # a list of stop-free, stemmed sentences
	# print stemedSentences

	print >> sys.stderr, "Building TF-IDF matrix..."
	(tfidf_vectorizer, tfidf_matrix) = tfidf(stemedSentences)

	print >> sys.stderr, "Reading in Questions..."
	quesfile = codecs.open(quests,encoding='utf-8')
	questions = readQuestion(quesfile) # a list of questions
	quesfile.close()
	# print questions

	print >> sys.stderr, "Removing stop words and steming the questions..."
	cleanQuestions = removeStopWords(questions,stopWords) # a list of stop-free questions
	stemedQuestions = steming(cleanQuestions) # a list of stop-free, stemmed questions

	print >> sys.stderr, "TFIDF searching... "
	negWords = {'no':1, 'not':1, 'never':1, 'none':1, 'neither':1, 'nothing':1, 'n\'t':1}

	# Write detailed output to a log file
	logName = article.split('.')[0]+'.log'
	logfile = open(logName,'w')

	for i in range(0,len(stemedQuestions)):
	# for q in stemedQuestions:
		logfile.write("======================================\n")
		logfile.write("\nQuestion:["+str(i+1)+']\t'+questions[i].strip().encode('utf-8')+"\n")
		ansSentenceIdx = tfidfSearch(tfidf_vectorizer, tfidf_matrix, stemedSentences, stemedQuestions[i])
		ansSentence = sentences[ansSentenceIdx]
		if isSimpleQuest(questions[i]):
			logfile.write( "Related sentence:\t" + ansSentence.strip().encode('utf-8')+"\n")
			logfile.write( "Answer:\t\t" + answerSimple(ansSentence,questions[i],negWords)+"\n")
			print answerSimple(ansSentence,questions[i],negWords)
		else:
			logfile.write( "Answer:\t\t"+ansSentence.encode('utf-8')+"\n")
			print ansSentence.strip().encode('utf-8')

if __name__ == '__main__':
	main()
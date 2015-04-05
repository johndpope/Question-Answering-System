import bs4
import re
import nltk
import coref.coref as coref
import coref.runArk as runArk
import glob
import codecs

class Article(object):

	def __init__(self,filename,arkfolder):
		self.filename = filename
		self.filetype = filename.split('.')[-1]
		self.content = self.shorten_file()
		self.arkfolder = arkfolder.strip('/')
		self.arkcontent = self.do_coref()
		self.list = self.generate_sentence_list()

	def shorten_file(self):
		filtered = ""
		if self.filetype == 'htm' or self.filetype == 'html':
			body = self.parse_html()
		else:
			body = (codecs.open(self.filename,encoding = 'utf-8')).read()

		lines = body.split('\n')
		for line in lines:
			line = line.strip()
			if len(line) == 0:continue
			if line == 'See also' or line == 'References':break
			if len(line.split()) <= 5 and line[-1] != '.':continue
			filtered += line + '\n\n'
		return filtered

	def parse_html(self):
	    try:
	        article_fd = open(self.filename).read()
	        article_fd = "<root>"+article_fd+"</root>" # trick arkref into doing entire doc
	        soup = bs4.BeautifulSoup(article_fd, "html.parser").root
	        resolved = re.sub("<.*?>", "", str(soup))
	    except:
	        resolved = open(self.filename).read()
	    resolved_u = resolved.decode("utf8")
	    resolved = resolved_u.encode('ascii', 'ignore')
	    return resolved

	def get_sentence_list(self,ark,stem,rmstem):
		if ark == 1:
			if rmstem == 1:
				return self.list['arkrmstop']
			elif stem == 1:
				return self.list['arkstem']
			else:
				return self.list['arkoriginal']
		else:
			if rmstem == 1:
				return self.list['rmstop']
			elif stem == 1:
				return self.list['stem']
			else:
				return self.list['original']		

	def generate_sentence_list(self):
		alllist = {}

		stopFilePath = "./Misc/stopword.txt"
		stopFile = open(stopFilePath,'r')
		stopWords = dict()
		for word in stopFile:
			stopWords[word.strip()] = 1
		stopFile.close()

		tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
		original = tokenizer.tokenize(self.content)
		arkoriginal = tokenizer.tokenize(self.arkcontent)

		stem = self.stemming(original)
		arkstem = self.stemming(arkoriginal)

		rmstop = self.remove_stop_words(original,stopWords)
		arkrmstop = self.remove_stop_words(arkoriginal,stopWords)

		rmstem = self.stemming(rmstop)
		arkrmstem = self.stemming(arkrmstop)

		alllist['original'] = original
		alllist['arkoriginal'] = arkoriginal
		alllist['stem'] = stem
		alllist['arkstem'] = arkstem
		alllist['rmstem'] = rmstem
		alllist['arkrmstem'] = arkrmstem

		return alllist

	def stemming(self,sentences):
		"""	
			Input:  a list of sentenses
			Output: a dict of sentenses with tokens stemed,
					key = stemed sentence, value = original sentence
		"""
		porter = nltk.PorterStemmer()
		stemmedSentences = []
		for sentence in sentences:
			tokens = nltk.word_tokenize(sentence)
			stemmedTokens = [porter.stem(t) for t in tokens]
			stemmedSentences.append(' '.join(stemmedTokens))
		return stemmedSentences

	def remove_stop_words(self,sentences,stopWords):
		"""Input: a list of sentences & a dict of stop words"""
		cleanSentences = []
		for sen in sentences:
			tokens = nltk.word_tokenize(sen)
			for i in range(0,len(tokens)):
				if tokens[i].lower() in stopWords:
					tokens[i] = ''
			cleanSentences += [' '.join(tokens).strip()]
		return cleanSentences

	def do_coref(self):
		files = glob.glob(self.arkfolder + '/*.txt')
		title = self.arkfolder + "/" + self.filename.split('/')[-1]
		title = title.replace('html','txt')
		title = title.replace('htm','txt')
		# print title
		if title not in files:
			# print "not there!!"
			coref.runCoref(self.content,self.filename,self.arkfolder)
		body = (codecs.open(title,encoding = 'utf-8')).read()
		return body
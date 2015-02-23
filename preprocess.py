import nltk
import sys
import glob
import errno
import codecs
import string,re
from xml.dom import minidom

def posTag(body,tokenizer):
	word_tag = {}

	sentences = tokenizer.tokenize(body)
	#print sentences
	for i in xrange(0,len(sentences)):
		tokens = nltk.word_tokenize(sentences[i])
		tagged = nltk.pos_tag(tokens)
		for j in tagged:
			word_tag.setdefault(j[0],set())
			word_tag[j[0]].add(j[1])				

	return word_tag

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def coreference(itemlist):
	regex = re.compile('[%s]' % re.escape(string.punctuation))
	id_term = {}
	for s in itemlist:
		entryid = s.attributes['entityid'].value
		if entryid in id_term:continue
		term = getText(s.childNodes)
		term = regex.sub('',term).strip()
		id_term[entryid] = term
	return id_term

def resolution(word_tag,id_term,itemlist):
	processed = ""
	for s in itemlist:
		terms = getText(s.childNodes).strip()
		tokens = terms.split()
		notin = False
		for i in tokens:
			if i not in word_tag:
				notin = True
		if notin == True:
			processed += terms + " "
			continue
		if len(tokens) > 1:
			if tokens[0][0] != 'a' and 'DT' in word_tag[tokens[0]] and 'NN' not in word_tag[tokens[1]]:
				entityid = s.attributes['entityid'].value
				if len(tokens) >=3 and 'NN' not in word_tag[tokens[2]]:
					residue = ""
					for i in xrange(2,len(tokens)):
						residue += tokens[i] + " "
					processed += id_term[entityid] + " " + residue
				else:
					processed += id_term[entityid] + " "
			else:
				processed += terms + " "
		elif 'PRP' in word_tag[terms]:
			entityid = s.attributes['entityid'].value
			processed += id_term[entityid] + " "
		elif 'PRP$' in word_tag[terms]:
			entityid = s.attributes['entityid'].value
			processed += id_term[entityid] + "'s "
	return processed

def main():
	tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
	datapath = sys.argv[1]
	files = glob.glob(datapath)
	for name in files:
		try:
			with codecs.open(name,encoding='utf-8') as f:
				body = f.read()
				word_tag = posTag(body,tokenizer)

				xmlfile = "xml/"+name.split("/")[1].split(".")[0]+".tagged"
				xmldoc = minidom.parse(xmlfile)
				itemlist = xmldoc.getElementsByTagName('mention')
				id_term = coreference(itemlist)

				to_write = resolution(word_tag,id_term,itemlist)
				fprocess = codecs.open("processed/"+name.split("/")[1],'w','utf-8')
				fprocess.write(to_write)
				fprocess.close()
		except IOError as exc:
			if exc.errno != errno.EISDIR:
				raise

if __name__ == '__main__':
	main()
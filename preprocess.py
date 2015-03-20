import sys
import glob
import errno
import codecs
import string,re
from bs4 import BeautifulSoup
from xml.dom import minidom

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
		term = regex.split(term)[0].strip()
		#term = regex.sub('',term).strip()
		id_term[entryid] = term
	return id_term

def resolution(pron,id_term,root):
	for s in root.find_all('mention'):
		if s.string != None and s.string.strip().lower() in pron:
			entityid = s["entityid"].strip()
			substitute = id_term[entityid]
			s.string.replace_with(substitute)
	processed = re.sub("<.*?>","",str(root))
	processed = unicode(processed,'utf-8')
	return processed

def main():
	pron = set(['she','her','hers','he','him','his','it','its','they','them','their',\
					'i','me','my','mine','we','our','ours','us','you','your','yours'])
	datapath = "xml/a1/*.tagged" # may change
	xmlfile = glob.glob(datapath)
	for name in xmlfile:
		print name
		try:
			with codecs.open(name,encoding='utf-8') as f:
				# print xmlfile
				xmldoc = minidom.parse(name)
				itemlist = xmldoc.getElementsByTagName('mention')
				id_term = coreference(itemlist)
				#print id_term
				
				body = f.read()
				root = BeautifulSoup(body).root

				to_write = resolution(pron,id_term,root)
				
		except Exception as exc:
			#print "exception in file: %s" % name 
			to_write = codecs.open(name,encoding='utf-8').read()
		#print to_write
		
		fprocess = codecs.open("processed/a1/"+name.split("/")[-1].split('.')[0]+".txt",'w','utf-8') #may change
		fprocess.write(to_write)
		fprocess.close()

if __name__ == '__main__':
	main()
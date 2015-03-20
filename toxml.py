import sys
import glob
import errno
import codecs

def main():
	filepath = "xml/a1/*.tagged"
	files = glob.glob(filepath)

	for name in files:
		try:
			with open(name) as f:
				body = f.read()
				body = "<root>"+body+"</root>"
				body = unicode(body,'utf-8',errors='ignore')
				f.close()
				f = codecs.open(name,'w',encoding='utf-8',errors='ignore')
				f.write(body)
				f.close()
		except IOError as exc:
			if exc.errno != errno.EISDIR:
				raise

if __name__ == '__main__':
	main()
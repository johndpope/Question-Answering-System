import subprocess
import glob
import sys

def main():
	filepath = sys.argv[1]
	filepath += "/*.txt"
	print filepath
	files = glob.glob(filepath)

	for name in files:
		print name
		command = "./coref/arkref.sh -input "+ name
		'''
		p = subprocess.Popen(command,shell=True)
		p.wait()
		'''
		f = open('runArk','w')
		p = subprocess.Popen(command,shell=True,stdout=f,stderr=f)
		p.wait()
		f.close()

if __name__ == '__main__':
	main()

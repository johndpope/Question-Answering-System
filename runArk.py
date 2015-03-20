import subprocess
import glob

def main():
	files = glob.glob("data/splits/*.txt")

	for name in files:
		command = "./arkref.sh -input "+ name
		p = subprocess.Popen(command,shell=True)
		p.wait()
		'''
		f = open('runArk','w')
		p = subprocess.Popen(command,shell=True,stdout=f,stderr=f)
		p.wait()
		f.close()
		'''

if __name__ == '__main__':
	main()
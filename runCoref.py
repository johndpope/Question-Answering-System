import subprocess
import glob
import sys

def main():
	source = sys.argv[1]
	destination = sys.argv[2]
	if source[-1] == '/':
		parent = source
		source += "*.txt"
	else:
		parent = source.replace(source.split("/")[-1],"")

	original = glob.glob(source)

	for name in original:
		one = name.split("/")[-1].split(".")[0]
		mkdir0 = "mkdir " + parent + "split_" + one
		p1_0 = subprocess.Popen(mkdir0,shell=True)
		p1_0.wait()
		mkdir1 = "mkdir "+ parent +"processed_" + one
		p1_1 = subprocess.Popen(mkdir1,shell=True)
		p1_1.wait()
		mkdir2 = "mkdir " + destination
		p1_2 = subprocess.Popen(mkdir2,shell=True)
		p1_2.wait()


		filegen = "python filegen.py " + name
		p2 = subprocess.Popen(filegen,shell=True)
		p2.wait()

		runArk = "python runArk.py " + parent + "split_" + one
		p3 = subprocess.Popen(runArk,shell=True)
		p3.wait()

		toxml = "python toxml.py "+ parent + "split_" + one
		p4 = subprocess.Popen(toxml,shell=True)
		p4.wait()
		
		preprocess = "python preprocess.py " + parent + "split_" + one 
		p5 = subprocess.Popen(preprocess,shell=True)
		p5.wait()
		
		merge = "python merge.py " + parent + "processed_" + one
		p6 = subprocess.Popen(merge,shell=True)
		p6.wait()

if __name__ == '__main__':
	main()
#!/usr/bin/python
import subprocess

def runCoref(content,filename,destination):
	print destination
	
	one = filename.split("/")[-1].split(".")[0]
	
	mkdir0 = "mkdir split_" + one
	p1_0 = subprocess.Popen(mkdir0,shell=True)
	p1_0.wait()
	mkdir1 = "mkdir processed_" + one
	p1_1 = subprocess.Popen(mkdir1,shell=True)
	p1_1.wait()
	mkdir2 = "mkdir " + destination
	p1_2 = subprocess.Popen(mkdir2,shell=True)
	p1_2.wait()

	i = 0
	paras = content.split('\n')

	for para in paras:
		if len(para.strip()) == 0:continue
		split = "split_" + one + "/" + str(i) + ".txt"
		fw = open(split,'w')
		fw.write(para)
		fw.close()
		i += 1

	runArk = "python coref/runArk.py split_" + one
	p3 = subprocess.Popen(runArk,shell=True)
	p3.wait()
	
	toxml = "python coref/toxml.py split_" + one
	p4 = subprocess.Popen(toxml,shell=True)
	p4.wait()
	
	preprocess = "python coref/preprocess.py split_" + one 
	p5 = subprocess.Popen(preprocess,shell=True)
	p5.wait()

	merge = "python coref/merge.py processed_" + one + " " + destination
	p6 = subprocess.Popen(merge,shell=True)
	p6.wait()

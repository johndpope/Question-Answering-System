import sys

filename = sys.argv[1]

i = 0
for line in open(filename):
	if len(line.strip())==0:continue
	if len(line.split())<2:continue
	split = 'data/split_' + filename.split("/")[-1].split(".")[0] + '/' + str(i) + '.txt'
	fw = open(split,'w')
	fw.write(line)
	fw.close()
	i+=1
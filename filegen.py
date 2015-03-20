i = 0
for line in open('data/a1.txt'):
	if len(line.strip())==0:continue
	if len(line.split())<2:continue
	fw = open('data/splits/a1_'+str(i)+'.txt','w')
	fw.write(line)
	fw.close()
	i+=1
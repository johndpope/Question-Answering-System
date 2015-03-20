import sys
import glob
import errno
import codecs

def sortFile(fileList):
	quickSortHelper(fileList,0,len(fileList)-1)

def quickSortHelper(fileList,start,end):
	if start < end:
		pivot = partition(fileList,start,end)

		quickSortHelper(fileList,start,pivot-1)
		quickSortHelper(fileList,pivot+1,end)

def partition(fileList,start,end):
	pivot = int(((fileList[start].split('/')[-1]).split('.')[0]).split('_')[-1])

	left = start + 1
	right = end

	done = False

	while not done:
		while left <= right and \
			int(((fileList[left].split('/')[-1]).split('.')[0]).split('_')[-1]) <= pivot:
		 	left += 1

		while int(((fileList[right].split('/')[-1]).split('.')[0]).split('_')[-1]) >= pivot \
			and right >= left:
		 	right -= 1

		if right < left:
		 	done = True
		else:
			temp = fileList[left]
			fileList[left] = fileList[right]
			fileList[right] = temp

	temp = fileList[start]
	fileList[start] = fileList[right]
	fileList[right] = temp

	return right

def main():
	filepath = 'processed/a1/*.txt' # THIS MAY CHANGE
	files = glob.glob(filepath)
	sortFile(files)

	fmerge = open('processed/a1.txt','a') # THIS MAY CHANGE

	for name in files:
		#print name
		try:
			with open(name) as f:
				body = f.read()
				body = body + '\n\n'
				fmerge.write(body)
		except IOError as exc:
			if exc.errno != errno.EISDIR:
				raise

	fmerge.close()

if __name__ == '__main__':
	main()
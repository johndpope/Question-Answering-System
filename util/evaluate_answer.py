import sys

def is_correct(test,ref):
	test = test.strip().strip('.')
	ref = ref.strip().strip('.')
	if test.lower() == ref.lower():
		return True
	if ref.lower() in test.lower():
		return True
	return False

def main():
	if len(sys.argv) < 4:
		print 'Usage: python evaluate_answer.py your_answer.txt ref_answer.txt question.txt\n'
		sys.exit(2)
	my_answer = open(sys.argv[1],'r')
	ref_answer = open(sys.argv[2],'r')
	question = open(sys.argv[3],'r')

	correctNum = 0
	totalNum = 0
	for test in my_answer:
		totalNum += 1
		ref = ref_answer.readline()
		quest = question.readline()
		if is_correct(test,ref):
			correctNum += 1
		else:
			print "=====> "
			print quest.strip()
			print "My answer:\t",test.strip()
			print "Correct answer:\t",ref.strip()
			# print "test.strip().strip('.'):",test.strip().strip('.')
			# print 'ref.strip()',ref.strip()

	my_answer.close()
	ref_answer.close()
	question.close()

	outstring = 'Correctely answered {} out of {} question, the accuracy is {}%.\n'\
				.format(correctNum,totalNum,correctNum*1.0/totalNum*100)
	print >> sys.stderr, outstring

if __name__ == '__main__':
	main()
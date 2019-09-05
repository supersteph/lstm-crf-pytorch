import os
import random
cwd = os.getcwd()

def getword(string):
	tag = string[-1]
	word = string[:-2]
	if tag == ">":
		word = string[:-6]
	return word

def random_line(array):
	return random.choice(array)

with open(cwd+'/tocorrupt.txt', 'r') as f:
	orig = open(cwd+'/final.txt', 'w')
	#other = open(cwd+'/training_data.word_to_idx', 'r')
	afile = open(cwd+'/training_data.word_to_idx', 'r').readlines()
	for item in f.readlines():
		pairs = item.strip().split(" ")
		prevword = ""
		topass = False
		for i, pair in enumerate(pairs):
			tag = pair[-1]
			word = pair[:-2]
			if topass>0:
				topass -= 1
				continue
			if tag == ">":
				word = pair[:-6]
				orig.write(word+" ")
			if tag == "0":
				orig.write(word+ " ")
			if tag == "2":
				if len(word) == 1:
					tag = "3"
				else:
					index = random.randint(0,len(word)-2)
					orig.write(word[:index]+word[index+1]+word[index]+word[index+2:]+" ")
			if tag == "3":
				curword = word
				while curword == word:
					curword = random_line(afile).strip()
				orig.write(curword+" ")
			if tag == "4":
				if prevword == "":
					for i in range(i,len(pairs)):
						if pairs[i][-1] == "4":
							orig.write(pairs[i][:-2]+ " ")
							prevword = word
				else:
					orig.write(prevword+" ")
			if tag == "5":
				nextword = getword(pairs[i+1])
				orig.write(word+nextword[0]+" "+nextword[1:]+" ")
				topass = 1
			if tag == "6":
				orig.write(word[:-1]+" "+word[-1]+getword(pairs[i+1])+" ")
				topass = 1
			if tag == "7":
				if i+3 == len(pairs):
					orig.write(getword(pairs[-1])+" "+word+" "+getword(pairs[i+1])+" ")
					topass = 2
				elif i+2 == len(pairs):
					orig.write(getword(pairs[-1])+" "+word+" ")
					topass = 1
				else:
					orig.write(getword(pairs[i+2])+" "+getword(pairs[i+3])+" "+word+" "+getword(pairs[i+1])+" ")
					topass = 3
			if tag == "8":
				orig.write("\t"+word+" ")


		orig.write("\n")
			


	orig.close()

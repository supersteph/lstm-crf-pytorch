import os
cwd = os.getcwd()

with open(cwd+'/write.txt', 'r') as f:
	orig = open(cwd+'/tocorrupt.txt', 'w')
	for item in f.readlines():
		pairs = item.strip().split(" ")
		isproblem = False
		for pair in pairs:
			tag = pair[-1]
			word = pair[:-2]
			if tag == "4":
				isproblem = True
			if tag == "1" and isproblem:
				tag = "4"
			orig.write(word+"/"+tag+" ")
		orig.write("\n")
			


	orig.close()
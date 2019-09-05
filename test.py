import os
import random
cwd = os.getcwd()


with open(cwd+'/final.txt', 'r') as f, open(cwd+'/first.txt', 'r') as o:
	for line1, line2 in zip(f,o):
		if line1==line2:
			print("problem")
			

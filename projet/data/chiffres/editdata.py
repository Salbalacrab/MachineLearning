import fileinput
import sys
import os
  
os.chdir("C:/Users/Salbalacrab/Desktop/ai-for-ev3-master/data/digits") # Changing to the directory you specified.
for file in os.listdir("C:/Users/Salbalacrab/Desktop/ai-for-ev3-master/data/digits"):
	if file.endswith(".txt"):
		for line in fileinput.input(file, inplace=True):
			sys.stdout.write('0,{l}'.format(l=line))
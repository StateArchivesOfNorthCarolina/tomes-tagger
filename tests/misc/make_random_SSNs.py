#!/usr/bin/env/python3

""" Makes random SSN numbers for testing; writes to file. """

# import modules.
import os
import sys
from random import randint

# set output file.
output = "PII.social_security_number__testData.txt"

# prevent overwrite of existing test data file.
if os.path.isfile(output):
	msg = "\nCannot continue.\n{} already exists.\n".format(output)
	sys.exit(msg)
	
# make SSN.
def makessn():
	temp = []
	def genssn(l=3):
		nums = ""
		for i in range(0,l):
			nums += str(randint(0,9))
		temp.append(nums)
	genssn(3)
	genssn(2)
	genssn(4)
	hyphen = randint(0,2)
	if hyphen == 0:
		sep = "-"
	elif hyphen == 1:
		sep = " "
	else:
		sep = ""
	ssn = sep.join(temp)
	return ssn

# call makessn() and write SSNs to file.
with open(output, "w") as f:
	for i in range(0,20):
		f.write(makessn())
		f.write("\n")
		# if randint(0,2) > 0:
			# f.write("\n")
		# else:
			# f.write(" ")

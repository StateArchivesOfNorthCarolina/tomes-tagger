from random import randint

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

with open("fake_ssns.txt", "w") as f:
	for i in range(0,100):
		f.write(makessn())
		if randint(0,2) > 0:
			f.write("\n")
		else:
			f.write(" ")

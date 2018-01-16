#!/usr/bin/env/python3

""" Creates file with random social-security-like numbers for testing. That is to say the
numbers may or may not meet the SSN specification. """

# import modules.
import os
from random import randint


def genSSN():
    """ Returns a random SSN-like number. """

    temp = []
    
    # generate random number with a given @length; append it (as string) to @temp.
    def genNum(length=3):
            nums = ""
            for i in range(0,length):
                nums += str(randint(0,9))
            temp.append(nums)
    
    # make random parts of SSN. 
    genNum(3)
    genNum(2)
    genNum(4)

    # randomly add a hyphen, whitespace, or nothing as the separator.
    hyphen = randint(0,2)
    if hyphen == 0:
        sep = "-"
    elif hyphen == 1:
        sep = " "
    else:
        sep = ""
    
    ssn = sep.join(temp)
    return ssn


def makeSSNFile(output="random_SSN_numbers.txt", total=20):
    """ Outputs @total random SSN-like numbers to @output file. """

    # prevent overwrite of exixting file. 
    if os.path.isfile(output):
        raise FileExistsError("Can't overwrite '{}'; please delete or rename it.".format(
            output))

    # write SSNS to @output.
    with open(output, "w") as out:
        
        for i in range(0,20):
            out.write(genSSN())
            out.write("\n")
            # if randint(0,2) > 0:
                # out.write("\n")
            # else:
                # out.write(" ")

    return


if __name__ == "__main__":
    makeSSNFile()


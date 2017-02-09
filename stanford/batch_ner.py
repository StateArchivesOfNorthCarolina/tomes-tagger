#!/usr/bin/env python2.7

import glob
import os

DIR = "D:\TOMES\TESTS\html2text" # where the emails are.
MAPPING = "mappings.txt" # the file with the regexner mapping.

emails = glob.glob(DIR + "/*.txt")
os.chdir("stanford-corenlp-full-2016-10-31")

i = 1
for email in emails:
    cmd = """java -cp "*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,regexner \
-file %s -regexner.mapping ../%s -outputDirectory %s -outputFormat json""" %(email, MAPPING, DIR)
    print
    print "*"*10
    print i, ": ", cmd
    os.system(cmd)
    i += 1
    #break

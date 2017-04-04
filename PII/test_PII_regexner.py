#!/usr/bin/env python3

# import modules
import os
from glob import glob
from pycorenlp import StanfordCoreNLP

# CoreNLP server must be running a la:
# java -mx2g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000
nlp = StanfordCoreNLP("http://localhost:9000")

def getNER(text, PII_type):
    mapping = "regexner_TOMES/" + PII_type + "__regexnerMappings.txt"
    properties = {"annotators":"tokenize, ssplit, pos, ner, regexner",
                 "outputFormat":"json",
                 "regexner.mapping":mapping}
    output = nlp.annotate(text, properties=properties)
    tokens = output["sentences"][0]["tokens"]
    
    words = [o["word"] for o in tokens]
    word = " ".join(words)
    
    ners = [o["ner"] for o in tokens]
    pii = [n for n in ners if n != "O"]
    ner = list(set(ners))
    ner_test = ner == [PII_type] 

    accuracy = len(pii)/len(tokens)
    return (word, ner, ner_test, accuracy)

#
header = ["PII_type", "Text", "NER", "NER_passed", "Accuracy", "Match", "Pass"]
print("\t".join(header))
PII = glob("*/")
for P in PII:
    P = P[:-1]
    os.chdir(P)
    test_data = open(P + "__testData.txt", "r")
    match_data = open(P + "__matchData.txt", "r")
    test_data = test_data.read().split("\n")
    match_data = match_data.read().split("\n")
    #print(test_data)

    for text in test_data:
        word, ner, ner_test, accuracy = getNER(text, P)
        match = word in match_data
        if ner_test and match:
            passed = True
        elif ner_test and not match:
            passed = False
        elif not ner_test and match:
            passed = False
        elif not ner_test and not match:
            passed = True
        report = [P, word, ner, ner_test, accuracy, match, passed]
        report = [str(r) for r in report]
        report = "\t".join(report)
        print(report)
    break
    
    

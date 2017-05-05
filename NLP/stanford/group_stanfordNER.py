""" Groups tokens by their NER tags. """

# import modules.
import os
import sys
import xml.etree.ElementTree as ET

# get CoreNLP XML output filename from user.
fi = raw_input("Stanford results XML filename: ")
f = "stanford-corenlp-full-2016-10-31/%s" %fi
print "grouping %s" %f
print

# parse XML file.
tree = ET.parse(f)
root = tree.getroot()
tokens = root.findall("document/sentences/sentence/tokens/token")

# group tokens by NER value.
i = 0
results = {}
for token in tokens:
    
    word = token.find("word").text
    ner = token.find("NER").text

    if i in results.keys() and ner == results[i]["NER"]:
        results[i]["text"].append(word)
    else:
        i = i + 1
        results[i] = {}
        results[i]["text"] = [word]
        results[i]["NER"] = ner

# print grouped results.
print "Results ..."
print
for r in results:
  text = " ".join(results[r]["text"])
  ner = results[r]["NER"]
  print "%s [%s]" %(text, ner)

# close upon user input.
print
input("Press (just about) any key to exit.")
exit()

import glob
import os
import sys

# get folder to process from command line argument.
try:
    inputs = sys.argv[1]
    outputs = sys.argv[2]
except:
    exit("You must pass both input and output folder names.")

# glob all .txt files in @folder.
texts = glob.glob(inputs + "/*.txt")

# run CoreNLP on all files.
i = 0
for text in texts:
    json = outputs + "/" + os.path.basename(text) + ".json"
    if os.path.isfile(json): # skip if output JSON file already exists.
        continue
    cmd = """java -cp "stanford-corenlp-full-2016-10-31/*" -Xmx2g edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize,ssplit,pos,lemma,ner,regexner -file {} -regexner.mapping mappings.txt -outputDirectory {} -outputFormat json"""
    cmd = cmd.format(text, outputs)
    #print(cmd)
    try:
        os.system(cmd)
    except:
        pass
    if i > 9999:
        exit()
    i += 1
    #break

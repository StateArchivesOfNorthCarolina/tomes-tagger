#!/usr/bin/env python3

# import modules.
import codecs
import glob
import json
import os
import sys
import time
from pycorenlp import StanfordCoreNLP

# get folder to process from command line argument.
try:
    inputs = sys.argv[1]
    outputs = sys.argv[2]
except:
    exit("You must pass both input and output folder names.")

# get whether or not to use CoreNLP server.
try:
    use_server = sys.argv[3]
except:
    exit("You must pass True or False to use the CoreNLP server (True) or not (False).")
    
if use_server == "True":
    use_server = True
    nlp = StanfordCoreNLP("http://localhost:9000")
else:
    use_server = False

# glob all .txt files in folder.
texts = glob.glob(inputs + "/*.txt")

# run CoreNLP on all files.
start_time = time.time() # start timing.
i = 0
for text in texts:
    
    # set output file; skip processing if already exists.
    json_file = outputs + "/" + os.path.basename(text) + ".json"
    if os.path.isfile(json_file): # skip if output JSON file already exists.
        continue
    
    # use command line CoreNLP if specified.
    if use_server != True:
        cmd = "java -cp \"stanford-corenlp-full-2016-10-31/*\" -Xmx2g "
        cmd += "edu.stanford.nlp.pipeline.StanfordCoreNLP "
        cmd += "-annotators tokenize,ssplit,pos,lemma,ner,regexner "
        cmd += "-file {} -regexner.mapping mappings.txt "
        cmd += "-outputDirectory {} -outputFormat json"
        cmd = cmd.format(text, outputs)
        #print(cmd)
        os.system(cmd)

    # otherwise, use CoreNLP server.
    else:
        options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
                  "outputFormat": "json",
                  "regexner.mapping": "regexner_TOMES/mappings.txt"}
                  # note: mappings file must exist in same dir as CoreNLP
                  # class path.
        f = codecs.open(text, encoding="utf-8")
        print("Processing {}".format(text))
        output = nlp.annotate(f.read(), properties=options)
        f.close()
        with codecs.open(json_file, mode="w", encoding="utf-8") as j:
            output = json.dumps(output, indent=2)
            j.write(output)

    # don't process over "i"-many files.
    #if i > 1:
	#    exit()
    i += 1
    #break

# stop timing; report.
stop_time = time.time()
total_time = stop_time - start_time
report = "\n\n{} files processed in {} seconds.".format(i, total_time)
print(report)


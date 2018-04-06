#!/bin/bash

# Depending on your version of CoreNLP, you might need to change the path below.
cd stanford-corenlp-full-2016-10-31
java -mx2g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9003 -timeout 50000 

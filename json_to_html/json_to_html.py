#!/usr/bin/env python3

"""
json_to_html.py:
Converts Stanford CoreNLP JSON output to HTML for basic viewing of email in browser.

example usage:
    $ python json_to_html.py ./json_files
"""

### import modules.
import codecs
import glob
import json
import os
import sys

### get path to JSON files from command line.
try:
    f = sys.argv[1]
except:
    exit("No path to JSON files passed.")

### create HTML file for each JSON file.
j_files = glob.glob(f + "/*.json")
for j_file in j_files:
    
    # skip over existing HTML files.
    if os.path.isfile(j_file + ".html"):
        print("Exiting: {}.html already exists.".format(j_file))
        continue
    
    # read file; load as JSON.
    print("Processing: {}.".format(j_file))
    fr = codecs.open(j_file, "r", encoding="utf-8").read()
    data = json.loads(fr)
    
    # set HTML headers; prepare to parse.
    html = ["<!DOCTYPE html><html><head><meta charset='utf-8' /><link rel='stylesheet' href='style.css'></link></head><body><div><pre><span>"]
    sentences = data["sentences"]
    current_ner = ""
    
    # write HTML.
    for sentence in sentences:
        tokens = sentence["tokens"]
       
        # determine if NER tag needs to be in HTML attribute.
        for token in tokens:
            originalText = token["originalText"]
            ner = token["ner"]
            after = token["after"]
            before = token["before"]

            if ner not in ["O", current_ner]:
                span = """</span>{}<span data-ner={}>{}""".format(before, ner, originalText)
            elif ner != current_ner:
                span = """</span>{}<span>{}""".format(before, originalText)
            else:
                span = "{}{}".format(before, originalText)
            
            html.append(span)
            current_ner = ner

    # close HTML.
    html.append("</span></pre></div></body></html>")

    # write HTML file.
    with codecs.open(f + ".html", "w", encoding="utf-8") as h:
        h.write("".join(html))


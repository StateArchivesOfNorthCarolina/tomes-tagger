#!/usr/bin/env python3

"""
json_to_html.py:
Converts Stanford CoreNLP JSON output to HTML for basic viewing of email in browser.

example usage:
    $ python json_to_html.py example.json # outputs example.json.html
"""

import codecs
import json
import sys
import os

try:
    f = sys.argv[1]
except:
    exit("You must pass a JSON file.")

if os.path.isfile(f + ".html"):
    print("Exiting: {}.html already exists.".format(f))
    exit()

fr = codecs.open(f, encoding="utf-8").read()
data = json.loads(fr)
html = ["<!DOCTYPE html><html><head><meta charset='utf-8' /><link rel='stylesheet' href='style.css'></link></head><body><div><pre><span>"]
sentences = data["sentences"]

current_ner = ""
for sentence in sentences:
    tokens = sentence["tokens"]
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
html.append("</span></pre></div></body></html>")

with codecs.open(f + ".html", "w", encoding="utf-8") as h:
    h.write("".join(html))


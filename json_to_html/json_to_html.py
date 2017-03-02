#!/usr/bin/env python3

"""
json_to_html.py:
Converts Stanford CoreNLP JSON output to HTML for basic viewing of email in browser.

example usage:
    $ python json_to_html.py example.json # outputs example.json.html
"""

import json
import sys

try:
    f = sys.argv[1]
except:
    exit("You must pass a JSON file.")

fr = open(f).read()
data = json.loads(fr)
html = ["<!DOCTYPE html><html><head><meta charset='utf-8' /><link rel='stylesheet' href='style.css'></link></head><body><div><pre>"]
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
html.append("</pre></div></body></html>")

with open(f + ".html", "w") as h:
    h.write("".join(html))


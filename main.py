#!/usr/bin/env python3

"""
This module reads an EAXS file and outputs a "tagged" version of the EAXS in which message
content has been run through an NLP application. The message and NER entities are encoded
in a defined schema.


TODO:
    - Move into class structure; instantiate other classes in __init__.
        - Example: HTMLToText() only needs to be instantiated once.
        - BTW: Is that composition?
    - Add timeout length to NLP if text is long.
        - For now, setting timeout when starting the server.
        Info: http://stackoverflow.com/a/36437157
    - Likely better to write output XML incrementally rather than all at once.
        - This will be easier in a class structure.
    - In the outputted EAXS: I'm seeing line breaks in other elements that were not there
    before.
    - Once a decision is made re: Comments, this would need to udpate ContentTypeComments,
    TransferEncodingComments, Description and/or DescriptionComments to say that this version
    of the EAXS has modifications VS the original.
"""

# import modules.
import base64
import codecs
import json
from lxml.etree import CDATA
from pycorenlp import StanfordCoreNLP
from lib.eaxs_to_etree import *
from lib.html_to_text import *
from lib.nlp_to_xml import *
from lib.nlp_to_stats import *
from lib.account_to_aip import *


# set globals.
CHARSET = "utf-8"
h2t = HTMLToText()
n2x = NLPToXML()


def getText(html):
    """ Returns string version of @html (str). """

    # alter DOM.
    html = ModifyHTML(html, "html5lib")
    html.shift_links()
    html.remove_images()
    html = html.raw()
    
    # convert HTML to text.
    text = h2t.text(html, is_raw=True)
    return text


def getNLP(text):
    """ Returns NLP/NER (JSON) for @text (str). """

    # set server and options.
    nlp = StanfordCoreNLP("http://localhost:9000")
    options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
               "outputFormat": "json",
               "regexner.mapping": "regexner_TOMES/mappings.txt"}
    
    # run NLP.
    try:
        nlp = nlp.annotate(text, properties=options)
    except Exception as e:
        exit(e)
    
    return nlp
    

def getTagged(jdict):
    """ Returns XML version of CoreNLP JSON: @jdict (dict). """

    # convert JSON To tagged XML.
    tagged = n2x.xml(jdict, return_string=True)
    return tagged


def tagEAXS(eaxs_file):
    """ Returns tagged version of @eaxs_file (str). """

    # get EAXS messages.
    eaxs = EAXSToEtree(eaxs_file)
    messages = eaxs.messages()

    # tag each message.
    for message in messages:

        print(message["message_id"].text) # test line.

        # get message text.
        text = message["content"].text
        if text == None:
            continue

        # decode Base64.
        if message["transfer_encoding"] != None:
            if message["transfer_encoding"].text == "base64":
                text = base64.b64decode(text)
                text = text.decode(encoding=CHARSET, errors="backslashreplace")
	
        # convert HTML to text.
        if message["content_type"].text == "text/html":
            text = getText(text)
	
        # run NLP; get tagged version of message.
        nlp = getNLP(text)
        tagged = getTagged(nlp)

        # set new message values.
        message["charset"].text = CHARSET
        message["content"].text = CDATA(tagged)
        message["content_type"].text  = "text/xml"
        message["transfer_encoding"].text = None
        break # test line.
    
    # return EAXS as etree element.
    eaxs = eaxs.to_etree()
    return eaxs


# TEST.
def main(eaxs_file):

    # make tagged version of EAXS.
    tagged = tagEAXS(eaxs_file)
    tagged = etree.tostring(tagged, pretty_print=True)
    tagged = tagged.decode("utf-8")
    
    # write tagged version to file.
    output = eaxs_file.replace(".xml", ".tagged.xml")
    with codecs.open(output, "w", encoding="utf-8") as f:
        f.write(tagged)

if __name__ == "__main__":
        
        import plac
        plac.call(main)


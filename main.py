#!/usr/bin/env python3

"""
TODO:
    - Move into class structure; instantiate other classes in __init__.
        - Example: HTMLToText() only needs to be instantiated once.
        - BTW: Is that composition?
    - Add timeout length to NLP if text is long.
    - Likely better to write output XML incrementally rather than all at once.
"""

# import modules.
import json
from pycorenlp import StanfordCoreNLP
from lxml import etree
from html_to_text.html_to_text import *
from nlp_to_xml.nlp_to_xml import *


def getText(html):
    """ Returns text version of @html (string). """

    # alter DOM.
    html = ModifyHTML(html, "html5lib")
    html.shift_links()
    html.remove_images()
    html = html.raw()
    
    # convert HTML to text.
    h2t = HTMLToText()
    text = h2t.text(html, is_raw=True)

    return text


def getNLP(text):
    """ Returns CoreNLP JSON string for @text (string). """

    nlp = StanfordCoreNLP("http://localhost:9000")
    options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
               "outputFormat": "json",
               "regexner.mapping": "regexner_TOMES/mappings.txt"}
    nlp = nlp.annotate(text, properties=options)
    nlp = json.dumps(nlp)
    
    return nlp
    

def getTagged(jdoc):
    """ Returns tagged version of CoreNLP JSON string: @jdoc (string). """

    # convert JSON To tagged XML.
    n2x = NLPToXML()
    tagged = n2x.xml(jdoc, is_raw=True, as_string=True)
    print(tagged) # test.
    
    return tagged


def tag_EAXS(eaxs_file):
    """ Returns tagged version EAXS file: @eaxs_file (string). """
    
    # set EAXS namespace prefix.
    ncdcr_ns = {"ncdcr": "http://www.archives.ncdcr.gov/mail-account"}

    # parse EAXS; leaving CData intact.
    parser = etree.XMLParser(strip_cdata=False)
    with open(eaxs_file, "rb") as eaxs:
        tree = etree.parse(eaxs, parser=parser)
    root = tree.getroot()

    # get folders.
    folders = root.findall("ncdcr:Folder", ncdcr_ns)

    i = 0
    for folder in folders: 

        # get messages; tag messages.
        messages = folder.findall("ncdcr:Message", ncdcr_ns)
        for message in messages:
            tagged_message = tag_message(message)
            if tagged_message != None:
                message = tagged_message
            i += 1
            if i > 10: # test.
                break
    
    return tree


def tag_message(message):
    """ Returns tagged string version of @message (<class 'lxml.etree._Element'>)."""

    # set EAXS namespace prefix.
    ncdcr_ns = {"ncdcr": "http://www.archives.ncdcr.gov/mail-account"}

    # temp ...
    id = message.find("ncdcr:MessageId", ncdcr_ns)
    #print(id.text)
    
    # only process text and HTML messages. 
    ctype = message.find("ncdcr:MultiBody/ncdcr:SingleBody/ncdcr:ContentType", ncdcr_ns)
    ctype = ctype.text
    if ctype not in ["text/html", "text/plain"]:
        return None
    
    # only process messages with actual text content.
    content = message.find("ncdcr:MultiBody/ncdcr:SingleBody/ncdcr:BodyContent/ncdcr:Content", ncdcr_ns)
    if content == None or content.text == None:
        return None
    
    # convert HTML to text if needed.
    text = content.text
    if ctype == "text/html":
        text = getText(text)

    # get NLP; make tagged version of content.
    nlp = getNLP(text)
    #stats = getStats(nlp)
    try:
        tagged = getTagged(nlp)
        content.text = etree.CDATA(tagged)
    except TypeError: # most likely when content is Base64 encoded.
        print(id.text)


    return message


# TEST.
def main():
    return tag_EAXS("D:/TOMES/DATA/zach.ambrose-CA1@nc.gov.xml")
    
if __name__ == "__main__":

    t = main()
    t = etree.tostring(t, pretty_print=True)
    t = t.decode("utf-8")
    
    import codecs
    with codecs.open("tagged_test.xml", "w", encoding="utf-8") as x:
        x.write(t)

    



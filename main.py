#!/usr/bin/env python3

"""
TODO:
    - Move into class structure; instantize other classes in __init__.
        - Is that composition?
"""

# import modules.
from html_to_text.html_to_text import *
from nlp_to_xml.nlp_to_xml import *
from pycorenlp import StanfordCoreNLP


def getText(html):
    """ """

    # alter DOM.
    html = ModifyHTML(html, "html5lib")
    html.shift_links()
    html.remove_images()
    html.raw()

    # convert HTML to text.
    h2t = HTMLToText()
    text = ht2.text(html.raw, is_raw=True)

    return text


def getNLP(text):
    """ """

    nlp = StanfordCoreNLP("http://localhost:9000")
    options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
                "outputFormat": "json",
                "regexner.mapping": "regexner_TOMES/mappings.txt"}
    nlp = nlp.annotate(text, properties=options)

    return nlp
    

def getTagged(json):
    """ """
    
    # convert JSON To tagged XML.
    n2x = NLPToXML()
    tagged = n2x.xml(json, is_raw=True, as_string=True)
    
    return tagged


def tag_EAXS(eaxs_file):
    """ """
    
    # set EAXS namespace prefix.
    ncdcr_ns = {"ncdcr": "http://www.archives.ncdcr.gov/mail-account"}

    # parse EAXS.
    tree = ET.parse(eaxs_file)
    root = tree.getroot()

    # get folders; get messages.
    folders = root.findall("ncdcr:Folder", ncdcr_ns)
    
    for folder in folders: 
        
        # tag messages.
        i = 0
        messages = folder.findall("ncdcr:Message", ncdcr_ns)
        for message in messages:
            tagged = tag_message(message)
            i += 1
            if i > 10: # test.
                break
    
    return tree


def tag_message(message):
    """ """

    # only alter text and HTML messages. 
    ctype = message.find("ncdcr:MultiBody/ncdcr:SingleBody/ncdcr:ContentType", ncdcr_ns)
    if ctype not in ["text/html", "text/plain"]:
        return None
    
    #
    content = message.find("ncdcr:MultiBody/ncdcr:SingleBody/ncdcr:BodyContent", ncdcr_ns)
    if content == None or content.text == None:
        return None
    
    #
    text = content.text
    if ctype == "text/html":
        text = getText(text)

    #
    nlp = getNLP(text)
    #stats = getStats(nlp)
    tagged = getTagged(nlp)

    return tagged

def main(eaxs_file):
    """ """
    
    pass


    


if __name__ == "__main__":
    main()

    
    



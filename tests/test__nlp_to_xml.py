#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import json
import logging
import unittest
import random
from lib.nlp_to_xml import *

# enable logging.
logging.basicConfig(level=logging.WARNING)

class Test_NLPToXML(unittest.TestCase):

    
    def setUp(self):
		
        # set attributes.
        self.n2x = NLPToXML()
        self.json_file = "sample_files/sampleCoreNLP.json"
    
 
    def test__validation(self):
        """ Is the sample tagged XML snippet valid? """
        
        # load JSON; convert to dict.
        with open(self.json_file) as f:
            jdoc = f.read()
            jdict = json.loads(jdoc)
        
        # validate XML.
        xml = self.n2x.xml(jdict)
        is_valid = self.n2x.validate(xml)
        
        # check if result is as expected.
        self.assertTrue(is_valid)


# CLI TEST.
def main(json_file: "CoreNLP JSON file"):
    
    "Prints tagged message version of CoreNLP JSON output.\
    \nexample: `py -3 test__nlp_to_xml.py sample_files\sampleCoreNLP.json`"
 
    # load JSON.
    with open(json_file) as f:
        jdoc = f.read()
        jdict = json.loads(jdoc)
    
    # convert JSON to dict.
    jdoc = open(json_file).read()
    jdict = json.loads(jdoc)

    # convert dict to XML.
    n2x = NLPToXML()
    xdoc = n2x.xstring(jdict)
    print(xdoc)


if __name__ == "__main__":
    
    import plac
    plac.call(main)


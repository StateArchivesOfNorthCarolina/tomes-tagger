#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import json
import unittest
import random
from lib.nlp_to_xml import *


class Test_NLPToXML(unittest.TestCase):

    
    def setUp(self):

        self.n2x = NLPToXML()
        self.json_file = "sample_files/sampleCoreNLP.json"

    
    def test__get_authority(self):

        n2x = self.n2x

        # test if authority assignment is as expected.
        tag = random.choice(self.n2x.custom_ner)
        ncdcr = n2x.get_authority(tag)
        stanford = n2x.get_authority("")
        self.assertEqual([ncdcr, stanford], ["ncdcr.gov", "stanford.edu"])

    
    def test__xml(self):
        
        n2x = self.n2x
        json_file = self.json_file

        # load JSON; convert to dict.
        with open(json_file) as f:
            jdoc = f.read()
            jdict = json.loads(jdoc)
        
        # test if XML is valid.
        xml = n2x.xstring(jdict)
        is_valid = n2x.validate(xml, is_raw=True)
        self.assertTrue(is_valid == True)


# CLI TEST.
def main(json_file: "Core NLP JSON file"):

    # load JSON; convert to dict.
    with open(json_file) as f:
        jdoc = f.read()
        jdict = json.loads(jdoc)
    
    jdoc = open(json_file).read()
    jdict = json.loads(jdoc)

    # convert JSON to XML and validate XML.
    n2x = NLPToXML()
    xdoc = n2x.xstring(jdict)
    print(xdoc)


if __name__ == "__main__":
    
    import plac
    plac.call(main)


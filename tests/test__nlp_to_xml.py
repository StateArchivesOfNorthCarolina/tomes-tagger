#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import json
import logging
import unittest
import random
from lib.nlp_to_xml import *


class Test_NLPToXML(unittest.TestCase):

    
    def setUp(self):

        # enable logging.
        logging.basicConfig(level=logging.DEBUG)
        
        self.n2x = NLPToXML()
        self.json_file = "sample_files/sampleCoreNLP.json"

    
    def test___get_authority(self):
        """ Are the authorities assigned correctly for NER tags? """

        # get authorities.
        tag = random.choice(self.n2x.custom_ner)
        ncdcr = self.n2x._get_authority(tag)
        stanford = self.n2x._get_authority("")

        # check if result is as expected.
        self.assertEqual([ncdcr, stanford], ["ncdcr.gov", "stanford.edu"])

    
    def test__validation(self):
        """ Is the sample tagged XML snippet valid? """
        
        # load JSON; convert to dict.
        with open(self.json_file) as f:
            jdoc = f.read()
            jdict = json.loads(jdoc)
        
        # validate XML.
        xml = self.n2x.xstring(jdict, header=False)
        is_valid = self.n2x.validate(xml, is_raw=True)
        
        # check if result is as expected.
        self.assertTrue(is_valid)


# CLI TEST.
def main(json_file: "CoreNLP JSON file"):

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


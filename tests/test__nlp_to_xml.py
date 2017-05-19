#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import unittest
import random
from lib.nlp_to_xml import *


class Test_NLPToXML(unittest.TestCase):

    
    def setUp(self):

        self.N2X = NLPToXML()
    

    def test__get_authority(self):

        tag = random.choice(self.N2X.custom_ner)
        ncdcr = self.N2X.get_authority(tag)
        stanford = self.N2X.get_authority("")
        self.assertEqual([ncdcr, stanford], ["ncdcr.gov", "stanford.edu"])

    
    def test__xml(self):
        
        with open("sample_files/sample_NER.json") as f:
            jdoc = f.read()
        xml = self.N2X.xml(jdoc)
        is_valid = self.N2X.validate(xml)
        self.assertTrue(is_valid == None)


if __name__ == "__main__":
    unittest.main()

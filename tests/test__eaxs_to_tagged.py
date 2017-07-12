#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import unittest
from lxml import etree
from lib.eaxs_to_tagged import *


class Test_EAXSToTagged(unittest.TestCase):


    def setUp(self):

        self.sample = "sample_files/sampleEAXS.xml"
        self.xsd = etree.parse("mail-account.xsd")

    
    def test__validation(self):
        """ Is it True that ... """

        #
        copy = lambda x: x
        
        #
        e2t = EAXSToTagged(copy, copy)
        tagged = e2t.get_tagged(self.sample)

        #
        validator = etree.XMLSchema(self.xsd)
        is_valid = validator.validate(tagged)

        # check if result is expected.
        self.assertEqual(True, is_valid)  


# CLI TEST.
def main(eaxs_file: "EAXS file"):

    #
    def mark(s):
        html, nlp = "HTML > NLP", "Text > NLP"
        if s[:len(nlp)] == nlp:
            return html # HTML conversion was run.
        else:
            return nlp # HTML conversion was not run.

    #
    e2t = EAXSToTagged(mark, mark)
    tagged = e2t.write_tagged(eaxs_file, "testTagged.xml")


if __name__ == "__main__":

    import plac
    plac.call(main)


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
        """ Is it sample EAXS document valid? """

        # function to return arg unaltered.
        copy = lambda x: x
        
        # make tagged EAXS.
        e2t = EAXSToTagged(copy, copy)
        tagged = e2t.get_tagged(self.sample)

        # validate tagged EAXS.
        validator = etree.XMLSchema(self.xsd)
        is_valid = validator.validate(tagged)

        # check if result is as expected.
        self.assertTrue(is_valid) 


# CLI TEST.
def main(eaxs_file: "input EAXS file", tagged_file: "tagged EAXS destination"):

    # function to mark processing for HTML emails VS. plain text.
    def mark(s):
        html, nlp = "HTML > NLP", "Text > NLP"
        if s[:len(nlp)] == nlp:
            return html # theoretical HTML conversion was run.
        else:
            return nlp # theoretical HTML conversion was NOT run.

    # write tagged EAXS to file.
    e2t = EAXSToTagged(mark, mark)
    tagged = e2t.write_tagged(eaxs_file, tagged_file)


if __name__ == "__main__":

    import plac
    plac.call(main)


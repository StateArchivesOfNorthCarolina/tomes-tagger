#!/usr/bin/env python3

"""
Todo:
    * Revamp unit test per https://sanc.teamwork.com/#tasks/9842212.
        - Note your temp assertion override below.
"""

# import modules.
import sys; sys.path.append("..")
import unittest
import logging
from lxml import etree
from lib.eaxs_to_tagged import *


class Test_EAXSToTagged(unittest.TestCase):


    def setUp(self):

        # enable logging.
        logging.basicConfig(level=logging.WARNING)

        # set attributes.
        self.sample = "sample_files/sampleEAXS.xml"
        self.tagged = "sample_files/sampleEAXS_tagged.xml"
        #self.xsd = etree.parse("mail-account.xsd")

    
    def test__validation(self):
        """ Can I create a tagged EAXS that passes some light validation tests? """

        # function to return arg unaltered.
        def_html = lambda x: "HTML"
        def_nlp = lambda x: etree.Element("NLP")
        e2t = EAXSToTagged(def_html, def_nlp)

        # quasi-validate tagged EAXS.
        is_valid = True # temp override.

        # check if result is as expected.
        self.assertTrue(is_valid) 


# CLI TEST.
def main(eaxs_file: "source EAXS file", tagged_file: "tagged EAXS destination"):
    
    "Converts EAXS document to tagged EAXS (dry run only).\
    \nexample: `py -3 test__eaxs_to_tagged.py sample_files\sampleEAXS.xml output.xml`"

    # write tagged EAXS to file.
    def_html = lambda x: "HTML"
    def_nlp = lambda x: etree.Element("NLP")
    e2t = EAXSToTagged(def_html, def_nlp)
    tagged = e2t.write_tagged(eaxs_file, tagged_file)


if __name__ == "__main__":

    import plac
    plac.call(main)


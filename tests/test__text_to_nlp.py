#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import json
import logging
import unittest
import random
from lib.text_to_nlp import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_TextToNLP(unittest.TestCase):
    """ Since our primary concern is making sure we can handle failed NER attempts, we'll test
    for those. """

    def setUp(self):
        
        # set attributes.
        self.host = "http://localhost"
        self.port = -1
        self.url = "{}:{}".format(self.host, self.port)
        self.corenlp = CoreNLP(url=self.url)
        self.t2n = TextToNLP(host=self.host, port=self.port)
    
 
    def test__failed_annotate(self):
        """ Since we can't connect to port -1, is a self.corenlp.Connection_Error raised? """
        
        # test calling CoreNLP.
        try:
            self.corenlp.annotate("")
            is_connection_error = False
        except self.corenlp.Connection_Error as err:
            is_connection_error = True
        
        # check if result is as expected.
        self.assertTrue(is_connection_error)


    def test__gets_empty_list(self):
        """ Since we can't connect to port -1, is an empty list returned? """

        results = self.t2n.get_ner("")
        self.assertTrue(results == [])


# CLI TEST.
def main(text="North Carolina", host="http://localhost", port=9003):
    
    "Prints list of NER results.\
    \nexample: `py -3 test__text_to_nlp.py 'Jane Doe'`"

    # get/print NER results.
    t2n = TextToNLP(host=host, port=port)
    ner = t2n.get_ner(text)
    print(ner)


if __name__ == "__main__":
    
    import plac
    plac.call(main)


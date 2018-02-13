#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import logging
import unittest
from tomes_tool.lib.text_to_nlp import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_TextToNLP(unittest.TestCase):
    """ Since our primary concern is making sure we can handle failed NER attempts, we'll test
    for those. """

    def setUp(self):
        
        # set attributes.
        self.host = "http://localhost:-1"
        self.corenlp = CoreNLP(host=self.host)
        self.t2n = TextToNLP(host=self.host)
    
 
    def test__failed_annotate(self):
        """ Since we can't connect to port -1, is a self.corenlp.Connection_Error raised? """
        
        # test calling CoreNLP.
        try:
            self.corenlp.annotate("")
            is_connection_error = False
        except ConnectionError as err:
            is_connection_error = True
        
        # check if result is as expected.
        self.assertTrue(is_connection_error)


    def test__gets_empty_list(self):
        """ Since we can't connect to port -1, is an empty list returned? """

        results = self.t2n.get_NER("")
        self.assertTrue(results == [])


# CLI TEST.
def main(text="North Carolina", host="http://localhost", port=9003):
    
    "Prints list of NER results.\
    \nexample: `py -3 test__text_to_nlp.py 'Jane Doe'`"

    # get/print NER results.
    t2n = TextToNLP(host=host, port=port, chunk_size=1)
    ner = t2n.get_NER(text)
    print(ner)


if __name__ == "__main__":
    
    import plac
    plac.call(main)


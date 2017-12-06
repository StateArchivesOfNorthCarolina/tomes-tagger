#!/usr/bin/env python3

""" This module converts ... 

Todo:

    
"""

# import modules.
import json
import logging
import pycorenlp
from textwrap import TextWrapper


class CoreNLP():
    """ ??? """

    def __init__(self, host="localhost", port=9003, 
            mapping_file="regexner_TOMES/mappings.txt", override_default_tags=True, omit_tags=[],
            *args, **kwargs):
        """ ??? 
        
        Args:
            
        """

        self.host="http://localhost:{}".format(port)
        self.props = {"annotators": "tokenize, ssplit, pos, ner, regexner",
         "outputFormat": "json"
         }
        self.nlp = pycorenlp.StanfordCoreNLP(self.host)

   
    def annotate(self, text):
        try:
            r = self.nlp.annotate(text, properties=self.props)
        except Exception as e:
            print("Can't talk to CoreNLP. Is it running?)
            raise self.CoreNLP_Error
        return r

    class CoreNLP_Error(Exception):
        """ Segments the modules exceptions."""
        pass


class TextToNLP():
    def __init__(self, corenlp):
        self.corenlp = corenlp
        # other stuff to specifically chunck and collect output ...

    def get_ner(self, text):
        results = []
        try:
            results = self.corenlp.annotate(text)
        except self.corenlp.CoreNLP_Error:
            print("Doh: CoreNLP server issue.")
            return

        for result in results:
            try:
                #a #force NamError
                result["bad_key"] #for TypeError
            except NameError as e:
                print("Doh: NameError")
                print(e)
            except TypeError as e:
                print("Doh: TypeError.")
                print(e)

corenlp_cls = CoreNLP("9002")
t2n = TextToNLP(corenlp_cls)
t2n.get_ner("Jane Doe") # CoreNLP_Error

print()

corenlp_cls = CoreNLP("9003")
t2n = TextToNLP(corenlp_cls)
t2n.get_ner("Jane Doe") # TypeError

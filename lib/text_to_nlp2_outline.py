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
            mapping_file="regexner_TOMES/mappings.txt", override_default_tags=True,
            *args, **kwargs):
        """ ??? 
        
        Args:
            
        """

        self.url="http://{}:{}".format(host, port)
        self.props = {"annotators": "tokenize, ssplit, pos, ner, regexner",
        "ner.useSUTime": "false", "ner.applyNumericClassifiers": "false",
        "outputFormat": "json"}
        self.nlp = pycorenlp.StanfordCoreNLP(self.url)

   
    def annotate(self, text):
        """ ??? """

        # ???
        try:
            results = self.nlp.annotate(text, properties=self.props)
        except Exception:
            # log error here.
            raise self.CoreNLP_Error("Can't talk to CoreNLP. Is it running?")
        
        return results

    class CoreNLP_Error(Exception):
        """ Segments the modules exceptions."""
        pass


class TextToNLP():
    """ ??? """


    def __init__(self, corenlp):
        """ ??? """
        
        self.corenlp = corenlp
        # other stuff to specifically chunck and collect output ...

   
    def get_ner(self, text):
        """ ??? """
        
        results = []
        try:
            results = self.corenlp.annotate(text)
        except self.corenlp.CoreNLP_Error:
            print("Doh: CoreNLP server issue.")
            return

        for result in results:
            try:
                print(results)
                #a #force NamError
                #result["bad_key"] #for TypeError
            except NameError as e:
                print("Doh: NameError")
                print(e)
            except TypeError as e:
                print("Doh: TypeError.")
                print(e)

corenlp_cls = CoreNLP(port=9002)
t2n = TextToNLP(corenlp_cls)
t2n.get_ner("Jane Doe") # CoreNLP_Error

print()

corenlp_cls = CoreNLP(port=9003)
t2n = TextToNLP(corenlp_cls)
t2n.get_ner("1/12/2005") # TypeError

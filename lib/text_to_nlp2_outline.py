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
            msg = "Unable to connect to CoreNLP at: {}".format(self.url)
            raise self.CoreNLP_Error(msg)
        
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
        
        ner = []
        try:
            results = self.corenlp.annotate(text)
        except self.corenlp.CoreNLP_Error as e:
            # log error here.
            print(e)
            return

        # ???
        if not isinstance(results, dict):
            # log error; do something to handle error.
            pass
        if "sentences" not in results.keys():
            # log error; do something to handle error.
            ner.append(None)

        sentences = results["sentences"]
        for sentence in sentences:

            tokens = sentence["tokens"]
            for token in tokens:
            
                # get required values.
                try:
                    text = token["originalText"]
                except KeyError:
                    text = token["word"]
                tag = token["ner"]
                if tag == "O":
                    tag = None
                trailing_space = token["after"]
                token_group = text, tag, trailing_space
                ner.append(token_group)

        return ner
                    

corenlp_cls = CoreNLP(port=9002)
t2n = TextToNLP(corenlp_cls)
t2n.get_ner("") # CoreNLP_Error

print()

corenlp_cls = CoreNLP(port=9003)
t2n = TextToNLP(corenlp_cls)
r = t2n.get_ner("1/12/2005 is a date that CoreNLP should not recognize now. Thanks Jane Doe.")
for i in r:
    print(i)


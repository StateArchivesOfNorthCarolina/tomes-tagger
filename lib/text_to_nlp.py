#!/usr/bin/env python3

""" This module converts plain text to Stanford CoreNLP's JSON output. It is a wrapper around
pycorenlp (https://github.com/smilli/py-corenlp).

Todo:
    * I don't think this should exit() on error. I think it should raise the error.
"""

# import modules.
import os
import subprocess
import urllib
from pycorenlp import StanfordCoreNLP


class TextToNLP():
    """ This module converts plain text to Stanford CoreNLP's JSON output. It is a wrapper
    around pycorenlp (https://github.com/smilli/py-corenlp). """


    def __init__(self, host="http://localhost", port=9000,
            mapping_file="regexner_TOMES/mappings.txt", *args, **kwargs):
        """ Sets instance attributes. 
        
        Args:
            - host (str): The base host URL for the CoreNLP server.
            - port (int): The host's port on which to run the CoreNLP server.
            - mapping_file (str): The relative path for the regexNER mapping file. This must
            be located within the CoreNLP server's file directory.
            - *args/**kwargs: Any additional, optional arguments to pass to pycorenlp.
        """

        # set CoreNLP server and options.
        self.host = "{}:{}".format(host, port)
        self.mapping_file = mapping_file
        self.annotator = StanfordCoreNLP(self.host, *args, **kwargs)
        self.options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
                "outputFormat": "json", "regexner.mapping": self.mapping_file}

    
    def get_NLP(self, text):
        """ Runs CoreNLP on @text.
        
        Args:
            - text (str): The text to send to CoreNLP.
            
        Returns:
            dict: The return value.
            The CoreNLP results.
        """
        
        try:
            nlp = self.annotator.annotate(text, properties=self.options)
            return nlp
        except Exception as e:
            exit(e)


if __name__ == "__main__":
    pass


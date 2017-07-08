#!/usr/bin/env python3

""" This module converts plain text to Stanford CoreNLP's JSON output. It is a wrapper around
pycorenlp (https://github.com/smilli/py-corenlp).
"""

# import modules.
import os
import subprocess
import urllib
from pycorenlp import StanfordCoreNLP


class TextToNLP():
    """ This module converts plain text to Stanford CoreNLP's JSON output. It is a wrapper
    around pycorenlp (https://github.com/smilli/py-corenlp). """


    def __init__(self, host="http://localhost", port=9000, mapping_file="regexner_TOMES/mappings.txt",
            *args, **kwargs):
        """ Sets attributes. 
        
        Args:
            - port (int): ???
            - timeout (int): ???
            - mapping_file (str): ???
            - *args/**kwargs: ???
        """

        # set annotation server and options.
        self.port = str(port)
        self.mapping_file = mapping_file
        self.host = ":".join([host, self.port])
        self.annotator = StanfordCoreNLP(self.host, *args, **kwargs)
        self.options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
                "outputFormat": "json",
                "regexner.mapping": self.mapping_file}


    def get_NLP(self, text):
        """ Returns Stanford CoreNLP results as dictionary.
        
        Args:
            - text (str): The text to subject to NLP.
            
        Returns:
            <class 'dict'>
        """
        
        annotator = self.annotator
        options = self.options
        
        # run NLP.
        try:
            nlp = annotator.annotate(text, properties=options)
            return nlp
        except Exception as e:
            exit(e)


# TEST.
def main():

    import json

    t2n = TextToNLP()
    results = t2n.get_NLP("TOMES")
    results = json.dumps(results, indent=2)
    print(results)


if __name__ == "__main__":
    main()


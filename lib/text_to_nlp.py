#!/usr/bin/env python3

""" This module converts plain text to Stanford CoreNLP's JSON output. It is a wrapper around
pycorenlp (https://github.com/smilli/py-corenlp).

TODO:
    - ???
"""

# import modules.
from pycorenlp import StanfordCoreNLP


class TextToNLP():
    """ This module converts plain text to Stanford CoreNLP's JSON output. It is a wrapper
    around pycorenlp (https://github.com/smilli/py-corenlp). """


    def __init__(self):
        """ Sets attributes. """

        # set annotation server and options.
        self.annotator = StanfordCoreNLP("http://localhost:9000")
        self.options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
                "outputFormat": "json",
                "regexner.mapping": "regexner_TOMES/mappings.txt"}


    def get_NLP(self, text):
        """ Returns Stanford CoreNLP results as dictionary.
        
        Args:
            - text (str): The text to subject to NLP.
            
        Returns:
            <class 'dict'>
        """
        
        annotator, options = self.annotator, self.options
        
        # run NLP.
        try:
            nlp = annotator.annotate(text, properties=options)
            return nlp
        except Exception as e:
            return e


# TEST.
def main():

    import json

    t2n = TextToNLP()
    results = t2n.get_NLP("TOMES")
    results = json.dumps(results, indent=2)
    print(results)


if __name__ == "__main__":
    main()


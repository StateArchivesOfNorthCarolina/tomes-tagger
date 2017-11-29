#!/usr/bin/env python3

""" This module converts plain text to Stanford CoreNLP's JSON output. It is a wrapper around
pycorenlp (https://github.com/smilli/py-corenlp).

Todo:
    * You need to document somewhere that chunking via textwrap will destroy line breaks. So,
    the tagged message can no longer be a whitespace-intact representation of the original
    message when chunking occurs.
    * Is 50k a good number for @chunk_size? If not, what should it be?
    * Currently, the "try/except" attempts to tag all chunks. Should the "for" loop be outside
    the "try/except"? IOW, should you "try" on each chunk instead of the entire @text?
        - CoreNLP will fail (I think) on blank text, so I still think you need to make sure
        the returned dict has a "sentences" key.
"""

# import modules.
import logging
import os
import subprocess
import urllib
from pycorenlp import StanfordCoreNLP
import socket
from textwrap import TextWrapper

CORENLP = socket.gethostbyname('corenlp-server')


class TextToNLP():
    """ This module converts plain text to Stanford CoreNLP's JSON output. It is a wrapper
    around pycorenlp (https://github.com/smilli/py-corenlp). """

    def __init__(self, host="http://{}".format(CORENLP), port=9003, chunck_size=50000,
            mapping_file="regexner_TOMES/mappings.txt", override_defaults=True, *args, 
            **kwargs):
        """ Sets instance attributes. 
        
        Args:
            - host (str): The base host URL for the CoreNLP server.
            - port (int): The host's port on which to run the CoreNLP server.
            - chunk_size (int): The maximum string length to send to CoreNLP at a time.
            - mapping_file (str): The relative path for the regexNER mapping file. This must
            be located within the CoreNLP server's file directory.
            - override_defaults (bool): If True, custom NER tags will override built-in tags
            when a string matches both tag patterns. If False, built-in tags will override
            custom tags.
            - *args/**kwargs: Any additional, optional arguments to pass to pycorenlp.
        """

        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # suppress "requests" module's logging if below a warning.
        # per: https://stackoverflow.com/a/11029841
        logging.getLogger("requests").setLevel(logging.WARNING) 
        
        # set CoreNLP server with options to get NER tags.
        self.host = "{}:{}".format(host, port)
        self.chunk_size = chunk_size
        self.mapping_file = mapping_file
        self.annotator = StanfordCoreNLP(self.host, *args, **kwargs)
        self.options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
                "outputFormat": "json",
                "regexner.mapping": self.mapping_file}

        # if specified, add option to override default tags.
        if override_defaults:
            default_tags = ["DATE", "DURATION", "LOCATION", "MISC", "MONEY", "NUMBER", "O",
             "ORDINAL", "ORGANIZATION", "PERCENT", "PERSON", "SET", "TIME"]
            self.options["regexner.backgroundSymbol"] =  ",".join(default_tags)


    def get_NER(self, text):
        """ Runs CoreNLP's NER tagger on @text.
        
        Args:
            - text (str): The text to send to CoreNLP's NER tagger.
            
        Returns:
            dict: The return value.
            The CoreNLP NER tagger results.
        """
        
        # set placeholder dictionary for NER results.
        ner = {"sentences": []}

        # if needed, break @text into smaller chunks.
        if len(text) > self.chunk_size:
            wrapper = TextWrapper(width=self.chunk_size, break_long_words=False, 
                    break_on_hyphens=False) 
            text = wrapper.wrap(text)
        else:
            text = [text]
        
        self.logger.info("Getting NER tags.")
        try:            
            for text_chunk in text:
                results = self.annotator.annotate(text_chunk, properties=self.options)
                ner["sentences"] += results["sentences"]
        except Exception as err:
            self.logger.error("Cannot get NER tags. Is the CoreNLP server working?")
            raise err

        return ner


if __name__ == "__main__":
    pass


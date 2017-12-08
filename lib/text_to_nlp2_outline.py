#!/usr/bin/env python3

""" This module converts ... 

Todo:

    
"""

# import modules.
import json
import logging
import pycorenlp
from textwrap import TextWrapper


class _CoreNLP():
    """ A private class to wrap pycorenlp (https://github.com/smilli/py-corenlp) and capture
    its exceptions with a custom error. """

    def __init__(self, url, mapping_file="", tags_to_override=[], *args, **kwargs):
        """ Sets instance attributes.

        Args:
            - url (str): The URL for the CoreNLP server (ex: "http://localhost:9003").
            - mapping_file (str): The relative path for the regexNER mapping file. This must
            be located within the CoreNLP server's file directory.
            - tags_to_override (list): The CoreNLP NER tag values to override if they conflict
            with a custom tag in @mapping_file. 
            -*args/**kwargs: Any additional, optional arguments to pass to pycorenlp.
        """

        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set CoreNLP server location and options.
        self.url = url
        self.mapping_file = mapping_file
        self.tags_to_override = tags_to_override
        self.options = {"annotators": "tokenize, ssplit, pos, ner, regexner",
        "ner.useSUTime": "false", "ner.applyNumericClassifiers": "false",
        "outputFormat": "json"}

        # if specified, add option to use mapping file.
        if self.mapping_file != "":
            self.options["regexner.mapping"] = self.mapping_file

        # if specified, add option to override default tags.
        if len(self.tags_to_override) > 0:
            self.options["regexner.backgroundSymbol"] = ",".join(self.tags_to_override)

        # compose instance of pycorenlp class.
        self.logger.info("Connecting to CoreNLP server at '{}' with options: {}".format(
            self.url, self.options))
        self.nlp = pycorenlp.StanfordCoreNLP(self.url, *args, **kwargs)

   
    def annotate(self, text):
        """ Runs CoreNLP's NER tagger on @text.
        
        Args:
            - text (str): The text to send to CoreNLP's NER tagger.
            
        Returns:
            dict: The return value.
            The CoreNLP NER tagger results.

        Raises:
            self.CoreNLP_Error: If pycorenlp fails.
        """

        # check that @text is a string.
        if not isinstance(text, str):
            self.logger.warning("Argument @text must be a string, got '{}' instead.".format(
                type(text).__name__))
            text = ""

        # get NER tag results.
        try:
            results = self.nlp.annotate(text, properties=self.options)
            return results
        except Exception:
            msg = "Unable to connect to CoreNLP at: {}".format(self.url)
            self.logger.error(msg)
            raise self.Connection_Error(msg)


    class Connection_Error(Exception):
        """ A custom error to trap connection errors from pycorenlp. """
        pass


class TextToNLP():
    """ ??? """


    def __init__(self, host="http://localhost", port=9003, 
            mapping_file="regexner_TOMES/mappings.txt", tags_to_override=["LOCATION", 
                "ORGANIZATION", "PERSON"]):
        """ ??? """
        
        # ???
        self.host = host
        self.port = port
        self.url="http://{}:{}".format(host, port)

        self._corenlp = _CoreNLP(self.url)

   
    def get_ner(self, text):
        """ ??? """
        
        # ???
        ner = []
        
        # ???
        try:
            results = self._corenlp.annotate(text)
        except self.corenlp.CoreNLP_Error as e:
            # log error here; don't print.
            print(e)
            return [None]

        # ???
        if not isinstance(results, dict):
            # log error; do something to handle error.
             return [None]
        if "sentences" not in results:
            # log error; do something to handle error.
            return [None]

        # ???
        sentences = results["sentences"]
        for sentence in sentences:

            if "tokens" not in sentence:
                # log error; do something to handle error.
                continue
            
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
                    

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)
    corenlp = _CoreNLP("http://localhost:9003")
    try:
        r = corenlp.annotate("1234 Jane")
        print(r)
    except corenlp.Connection_Error as e:
        print(e)


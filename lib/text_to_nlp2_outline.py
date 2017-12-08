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

        # compose instance of main pycorenlp class.
        self.nlp = pycorenlp.StanfordCoreNLP(self.url, *args, **kwargs)

   
    def annotate(self, text):
        """ Runs CoreNLP's NER tagger on @text.
        
        Args:
            - text (str): The text to send to CoreNLP's NER tagger.
            
        Returns:
            dict: The return value.
            The CoreNLP NER tagger results.

        Raises:
            - TypeError: If @text is not a string.
            - self.Connection_Error: If pycorenlp cannot connect to the CoreNLP server.
        """

        # verify that @text is a string.
        if not isinstance(text, str):
            msg = "Argument @text must be a string, got '{}' instead.".format(
                    type(text).__name__)
            raise TypeError(msg)

        # get NER tag results.
        try:
            results = self.nlp.annotate(text, properties=self.options)
            return results
        except Exception as e:
            msg = "Unable to connect to CoreNLP at: {}".format(self.url)
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
        
        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set server location attributes.
        self.host = host
        self.port = port
        self.url="{}:{}".format(host, port)

        # compose instance of CoreNLP wrapper class.
        self.corenlp = _CoreNLP(self.url)

   
    def get_ner(self, text):
        """ ??? """
        
        # prepare output containers.
        ner = []
        failed_ner = [None]
        
        # get NER tags.
        try:
            results = self.corenlp.annotate(text)
        except (TypeError, self.corenlp.Connection_Error) as e:
            self.logger.error(e)
            return failed_ner

        # ensure @results is correct data type.
        if not isinstance(results, dict):
            self.logger.warning("CoreNLP wrapper returned '{}', expected dictionary.".format(
                type(results).__name__))
            return failed_ner
        
        # ensure @results contains required key.
        if "sentences" not in results:
            self.logger.warning("CoreNLP response is missing required field 'sentences'.")
            return failed_ner

        # loop through data; append necessary values to @ner.
        sentences = results["sentences"]
        for sentence in sentences:

            tokens = sentence["tokens"]
            for token in tokens:

                try:
                    text = token["originalText"]
                except KeyError:
                    text = token["word"]
                
                tag = token["ner"]
                if tag == "O": # because CoreNLP uses "O" for a null NER tag.
                    tag = None
                
                trailing_space = token["after"]
                
                # append values as tuple.
                token_group = text, tag, trailing_space
                ner.append(token_group)

        return ner
                    

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)
    t2n = TextToNLP()
    res = t2n.get_ner("1234 is a number. Jane Doe is married to John Doe.")
    for w, t, s in res:
        print("{} [{}]".format(w, t))

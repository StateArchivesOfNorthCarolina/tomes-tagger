#!/usr/bin/env python3

""" This module contains a class to extract tokens and their corresponding NER tags from a 
given text using Stanford's CoreNLP. It also contains a class to wrap pycorenlp 
(https://github.com/smilli/py-corenlp) and capture its exceptions more explicitly.

Todo:
    * ???
"""

# import modules.
import json
import logging
import pycorenlp
from textwrap import TextWrapper


class CoreNLP():
    """ A class to wrap pycorenlp (https://github.com/smilli/py-corenlp) and capture its 
    exceptions more explicitly. """

    def __init__(self, url, mapping_file="", tags_to_override=[], *args, **kwargs):
        """ Sets instance attributes.

        Args:
            - url (str): The URL for the CoreNLP server (ex: "http://localhost:9003").
            - mapping_file (str): The relative path for the regexNER mapping file. This must
            be located within the CoreNLP server's file directory.
            - tags_to_override (list): The CoreNLP NER tag values to override if they 
            conflict with a custom tag in @mapping_file. 
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
        """ A custom error class for trapping connection errors from pycorenlp. """
        pass


class TextToNLP():
    """ A class to extract tokens and their corresponding NER tags from a given text using
    Stanford's CoreNLP. """


    def __init__(self, host="http://localhost", port=9003, chunk_size=50000,
            mapping_file="regexner_TOMES/mappings.txt", tags_to_override=["LOCATION", 
                "ORGANIZATION", "PERSON"]):
        """ Sets instance attributes.

        Args:
            - host (str): The base host URL for the CoreNLP server.
            - port (int): The host's port on which to run the CoreNLP server.
            - chunk_size (int): The maximum string length to send to  at a time.
            - mapping_file (str): See help(CoreNLP) for more info.
            - tags_to_override (list): See help(CoreNLP) for more info.
            """
        
        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set server location attributes.
        self.host = host
        self.port = port
        self.url="{}:{}".format(host, port)

        # compose instance of CoreNLP wrapper class.
        self.nlp = CoreNLP(self.url, mapping_file, tags_to_override)

   
    def get_ner(self, text):
        """ Performs tokenization and NER tagging on @text.
        
        Args:
            - text (str): The text to tokenize and tag.
            
        Returns:
            list: The return value.
            The NER tagger results as a list of tuples.
            The first item in the tuple is a token. The second and third items are the NER 
            tag value and the trailing whitespace chracter, respectively. All items are 
            strings.
        """
        
        # prepare output container.
        ner = []

        # pre-prepare data to use during failures.
        failed_ner = []
        failed_token_group = "", "", ""
        
        # get NER tags.
        try:
            results = self.corenlp.annotate(text)
        except (TypeError, self.nlp.Connection_Error) as e:
            self.logger.error(e)
            return failed_ner

        # ensure @results is correct data type.
        if not isinstance(results, dict):
            self.logger.warning("CoreNLP wrapper returned '{}', expected dictionary.".format(
                type(results).__name__))
            return failed_ner
        
        # verify @results contains required key.
        if "sentences" not in results:
            self.logger.warning("CoreNLP response is missing required field 'sentences'.")
            return failed_ner

        # loop through data; append necessary values to @ner.
        sentences = results["sentences"]
        for sentence in sentences:

            # verify @sentence contains required key.
            if "tokens" not in sentence:
                msg = "No 'tokens' field not found; appending empty values to output."
                self.logger.warning(msg)
                ner.append(failed_token_group)
                continue

            # get values.
            tokens = sentence["tokens"]
            for token in tokens:

                # determine key to use for original text.
                text_key = "originalText"
                if text_key not in token:
                    text_key = "word"

                # get values.
                try:
                    text, tag, tspace = token[text_key], token["ner"], token["after"]
                except KeyError as e:
                    self.logger.error(e)
                    self.logger.warning("Token data not found; appending empty values to \
                            output.")
                    text, tag, tspace = failed_token_group
                
                # overwrite CoreNLP's use of "O" for a null NER tag.
                if tag == "O":
                    tag = ""

                # append final values to @ner.
                token_group = text, tag, tspace
                ner.append(token_group)

        return ner
                    

if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)
    t2n = TextToNLP()
    res = t2n.get_ner("1 Jane Doe.")
    for r in res:
        print(r)

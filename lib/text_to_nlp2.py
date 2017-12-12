#!/usr/bin/env python3

""" This module contains a class to extract tokens and their corresponding NER tags from a 
given text using Stanford's CoreNLP. It also contains a class to wrap pycorenlp 
(https://github.com/smilli/py-corenlp) and capture its exceptions more explicitly.

Todo:
    * Add logging to CoreNLP()???
    * You still need a try/except around each chunk attempt in the decorator.
    * If we have to log a response, should we limit the length of what we return (to reduce
    excessive logging)?
        - It's probably better to have a private function you can pass the repsonse to. I 
        don't like how I'm encoding/decoding under two separate conditions.
    * Jeremy asks "What is a sane return that won't break the workflow or can we fix?
        - I think is specific if a dict isn't returned, but also points to some server
        timeout, etc. This might be where we need to maintain a running list of problem
        message ids.
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

        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # suppress "requests" module's logging if below a warning.
        # per: https://stackoverflow.com/a/11029841
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        
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
            logger_charset="ascii", mapping_file="regexner_TOMES/mappings.txt", 
            tags_to_override=["LOCATION", "ORGANIZATION", "PERSON"]):
        """ Sets instance attributes.

        Args:
            - host (str): The base host URL for the CoreNLP server.
            - port (int): The host's port on which to run the CoreNLP server.
            - chunk_size (int): The maximum string length to send to  at a time.
            - logger_charset (str): Encoding used if an erroneous CoreNLP response needs to be
            logged.
            - mapping_file (str): See "help(CoreNLP)" for more info.
            - tags_to_override (list): See "help(CoreNLP)" for more info.
            """
        
        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.host = host
        self.port = port
        self.url = "{}:{}".format(host, port)
        self.chunk_size = chunk_size
        self.logger_charset = logger_charset
        self.mapping_file = mapping_file
        self.tags_to_override = tags_to_override

        # compose instance of CoreNLP wrapper class.
        self.corenlp = CoreNLP(self.url, self.mapping_file, self.tags_to_override)


    def __get_ner_decorator(def__get_ner):
        """ A decorator for self.get_ner() that splits text into chunks if the string passed
        to self.get_ner() exceeds self.chunk_size in length. 
        
        Args:
            - def__get_ner (function): An alias intended for self.get_ner().

        Returns:
            function: The return value.

        Raises:
            - TypeError: If @text passed to get_ner() is not a string.
        """

        def wrapper(self, text):

            ner_results = []
            
            # verify that @text is a string.
            if not isinstance(text, str):
                msg = "Argument @text must be a string, got '{}' instead.".format(
                        type(text).__name__)
                raise TypeError(msg)

            # if needed, break @text into smaller chunks.
            if len(text) > self.chunk_size:
                self.logger.debug("@text exceeds chunk size of: {}.".format(self.chunk_size))
                wrapper = TextWrapper(width=self.chunk_size, break_long_words=False, 
                        break_on_hyphens=False, drop_whitespace=False, 
                        replace_whitespace=False) 
                text_list = wrapper.wrap(text)
            else:
                text_list = [text]

            # get NER tags for each item and add results to @ner.
            i = 1
            total_chunks = len(text_list)
            for text_chunk in text_list:
                self.logger.debug("Getting NER tags for chunk {} of {}.".format(i, 
                    total_chunks))
                tokenized_tagged = def__get_ner(self, text_chunk)
                ner_results += tokenized_tagged
                i += 1

            return ner_results

        return wrapper


    @__get_ner_decorator
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
  
        # prepare output containers.
        output = []

        # pre-prepare data to use during failures.
        failed_output = []
        
        # get NER tags.
        results = {}
        try:
            results = self.corenlp.annotate(text)
        except (TypeError, self.corenlp.Connection_Error) as e:
            self.logger.error(e)
            return failed_output

        # ensure @results is correct data type, otherwise return.
        if not isinstance(results, dict):
            results_err = results.encode(self.logger_charset, errors="ignore").decode()
            self.logger.warning("CoreNLP wrapper returned '{}', expected dictionary.".format(
                type(results).__name__))
            self.logger.debug("CoreNLP response: {}".format(results_err))
            return failed_output

        # verify @results contains required key, otherwise return.
        if "sentences" not in results:
            results_err = str(results).encode(self.logger_charset, errors="ignore").decode()
            self.logger.warning("CoreNLP response is missing required field 'sentences'.")
            self.logger.debug("CoreNLP response: {}".format(results_err))
            return failed_output

        # loop through data; append necessary values to @ner.
        sentences = results["sentences"]

        if sentences == []:
            output.append(("", "", text))
            return output

        for sentence in sentences:

            # verify @sentence contains required key.
            if "tokens" not in sentence:
                msg = "'tokens' field not found; nothing to append to output."
                self.logger.warning(msg)
                continue

            # get token values.
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
                    self.logger.warning("Token data not found; nothing to append to output.")
                    continue
                
                # overwrite CoreNLP's use of "O" for a null NER tag.
                if tag == "O":
                    tag = ""

                # append final values to @ner.
                token_group = text, tag, tspace
                output.append(token_group)

        return output


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    t2n = TextToNLP(port=9003, chunk_size=1)
    s = "Jack Jill\n\t\rpail"
    #s = None
    print(repr(s))
    res = t2n.get_ner(s)
    print(res)


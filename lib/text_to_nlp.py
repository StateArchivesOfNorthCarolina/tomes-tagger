#!/usr/bin/env python3

""" This module contains a class to extract tokens and their corresponding NER tags from a 
given text using Stanford's CoreNLP. It also contains a class to wrap pycorenlp 
(https://github.com/smilli/py-corenlp) and capture its exceptions more explicitly.

Todo:
    * Jeremy asks "What is a sane return that won't break the workflow or can we fix?
        - Nitin update: this new version of text_to_nlp is really trying to guarantee a list
        is returned regardless of what happens. So we could lose data, but it shouldn't break
        the workflow.
    * Remove __main__ test snippet when ready.
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

        # suppress third party logging that is not a warning or higher.
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
            - self.Connection_Error: If pycorenlp can't connect to the CoreNLP server.
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
        except Exception as err:
            msg = "Can't connect to CoreNLP at: {}".format(self.url)
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
            - host (str): The base URL for the CoreNLP server.
            - port (int): The port on which to run the CoreNLP server.
            - chunk_size (int): The maximum string length to send to CoreNLP at once.
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
        self.mapping_file = mapping_file
        self.tags_to_override = tags_to_override

        # compose instance of CoreNLP wrapper class.
        self.corenlp = CoreNLP(self.url, self.mapping_file, self.tags_to_override)


    def _encode_bad_response(self, response, charset="ascii", max_length=500):
        """ In the event CoreNLP returns an erroneous or unexpected @response; this function
        can convert that response to a string for logging purposes. The string will be encoded
        using @charset as the encoding. The returned value will be truncated if its length
        exceeds @max_length.

        Args:
            response (str): The response from CoreNLP.
            charset (str): The character encoding with which to encode @response.
            max_length (int): The maximum string length for the return value.

        Returns:
            str: The return value.
        """

        # verify @response is a string; decode @response.
        if not isinstance(response, str):
            response = str(response)
        response = response.encode(charset, errors="ignore").decode()
        
        # if needed, truncate @response.
        if len(response) > max_length:
            self.logger.debug("Response exceeds @max_length of '{}'; truncating.".format(
                max_length))
            response = response[:max_length] + " ..."

        return response


    def __preprocess_ner_requests(def__get_ner):
        """ A decorator for self.get_ner() that splits text into chunks if the string passed
        to self.get_ner() exceeds self.chunk_size in length. 
        
        Args:
            - def__get_ner (function): An alias intended for self.get_ner().

        Returns:
            function: The return value.

        Raises:
            - TypeError: If @text passed to get_ner() is not a string.
        """

        def preprocessor(self, text):

            # prepare output container.
            ner_output = []
            
            # verify that @text is a string.
            if not isinstance(text, str):
                self.logger.error("Argument @text must be a string, got: {}".format(
                    type(text).__name__))
                self.logger.warning("Falling  back to empty output.")
                return []

            # if needed, break @text into smaller chunks.
            if len(text) <= self.chunk_size:
                text_list = [text]
            else:
                self.logger.info("Text exceeds chunk size of: {}".format(self.chunk_size))
                try:
                    wrapper = TextWrapper(width=self.chunk_size, break_long_words=False, 
                        break_on_hyphens=False, drop_whitespace=False, expand_tabs=False, 
                        replace_whitespace=False) 
                    text_list = wrapper.wrap(text)
                except Exception as err:
                    self.logger.error(err)
                    self.logger.error("Failed to chunk text.")
                    self.logger.warning("Falling back to empty output.")
                    return []

            # get NER tags for each item and add results to @ner_output.
            i = 1
            total_chunks = len(text_list)
            
            for text_chunk in text_list:
                self.logger.info("Getting NER tags for chunk {} of {}.".format(i, 
                    total_chunks))
                try:
                    tokenized_tagged = def__get_ner(self, text_chunk)
                except Exception as err:
                    self.logger.error(err)
                    self.logger.error("Failed to get NER tags for chunk.")
                    self.logger.warning("Fallign back to empty output for chunk.")
                    tokenized_tagged = []
                ner_output += tokenized_tagged
                i += 1

            return ner_output

        return preprocessor


    @__preprocess_ner_requests
    def get_ner(self, text):
        """ Performs tokenization and NER tagging on @text.
        
        Args:
            - text (str): The text to tokenize and tag.
       
        Returns:
            list: The return value.
            The NER tagger results as a list of tuples.
            The first item in the tuple is a token. The second and third items are the NER 
            tag value and the trailing whitespace, respectively. All items are strings.
        """
  
        # prepare output container.
        ner_output = []

        # get NER tags.
        results = {}
        try:
            results = self.corenlp.annotate(text)
        except self.corenlp.Connection_Error as err:
            self.logger.error(err)
            self.logger.warning("Falling back to empty output.")
            return []

        # ensure @results is correct data type.
        if not isinstance(results, dict):
            self.logger.warning("CoreNLP wrapper returned '{}', expected dictionary.".format(
                type(results).__name__))
            self.logger.warning("Falling back to empty output.")
            results_err = self._encode_bad_response(results)
            self.logger.debug("CoreNLP response: {}".format(results_err))
            return []

        # verify @results contains required key.
        if "sentences" not in results:
            self.logger.warning("CoreNLP response is missing required field 'sentences'.")
            self.logger.warning("Falling back to empty output.")
            results_err = self._encode_bad_response(results)
            self.logger.debug("CoreNLP response: {}".format(results_err))
            return []

        # get values to loop through.
        sentences = results["sentences"]

        # if @sentences is null, return tuple with @text value as last item.
        # Why? It appears CoreNLP will return a null when asked to tag only whitespace.
        if sentences == []:
            ner_output.append(("", "", text))
            return ner_output

        # loop through data; append necessary values to @ner_output.
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

                # get tuple values.
                try:
                    text, tag, tspace = token[text_key], token["ner"], token["after"]
                except KeyError as err:
                    self.logger.error(err)
                    self.logger.warning("Token data not found; nothing to append to output.")
                    continue
                
                # overwrite CoreNLP's use of "O" for a null NER tag.
                if tag == "O":
                    tag = ""

                # append final values to @ner_output.
                token_group = text, tag, tspace
                ner_output.append(token_group)

        return ner_output


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    t2n = TextToNLP(port=9003, chunk_size=5)
    s = "Jack Jill\n\t\rpail"
    #s = None
    print(repr(s))
    res = t2n.get_ner(s)
    print(res)


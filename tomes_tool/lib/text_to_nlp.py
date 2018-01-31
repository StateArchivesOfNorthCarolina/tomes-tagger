#!/usr/bin/env python3

""" This module contains a class to extract tokens and their corresponding NER tags from a 
given text using Stanford's CoreNLP. It also contains a class to wrap pycorenlp 
(https://github.com/smilli/py-corenlp) and capture its exceptions more explicitly. """

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
            mapping_file="regexner_TOMES/mappings.txt", tags_to_remove=["DATE", "DURATION",
                    "MISC", "MONEY", "NUMBER", "O", "ORDINAL", "PERCENT", "SET", "TIME"]):
        """ Sets instance attributes.

        Args:
            - host (str): The base URL for the CoreNLP server.
            - port (int): The port on which to run the CoreNLP server.
            - chunk_size (int): The maximum string length to send to CoreNLP at once. Increase
            it at your own risk.
            - mapping_file (str): See "help(CoreNLP)" for more info.
            - tags_to_remove (list): If CoreNLP returns one on these NER tags, the tag will be
            replaced with an empty string.
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
        self.tags_to_remove = tags_to_remove
        self.stanford_tags = ["DATE", "DURATION", "LOCATION", "MISC", "MONEY", "NUMBER", "O",
                "ORDINAL", "ORGANIZATION", "PERCENT", "PERSON", "SET", "TIME"]
        
        # compose instance of CoreNLP wrapper class.
        self.corenlp = CoreNLP(self.url, mapping_file=self.mapping_file, 
                tags_to_override=self.stanford_tags)


    @staticmethod
    def _get_outer_space(text):
        """ Returns the leading and trailing whitespace for a given @text. 
        
        Args:
            text (str): The string from which to extract leading and trailing whitespace.
            
        Returns:
            tuple: The return value.
            The first item (str) is @text's leading whitespace.
            The second item (str) is @text's trailing whitespace.
        """

        # assume values.
        leading_space, trailing_space = "", ""

        # get length of leading and trailing whitespace.
        leading_distance = len(text) - len(text.lstrip())
        trailing_distance = len(text) - len(text.rstrip())

        # if leading or trailing space exists, update return values.
        if leading_distance > 0 and leading_distance < len(text):
            leading_space = text[:leading_distance]
        if trailing_distance > 0 and trailing_distance < len(text):
            trailing_space = text[-trailing_distance:]

        return (leading_space, trailing_space)


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
        response = response.encode(charset, errors="ignore").decode(charset, errors="ignore")
        
        # if needed, truncate @response.
        if len(response) > max_length:
            self.logger.debug("Response exceeds @max_length of '{}'; truncating.".format(
                max_length))
            response = response[:max_length] + " ..."

        return response


    def __process_NER_requests(def__get_NER):
        """ A decorator for self.get_NER() that splits text into chunks if the string passed
        to self.get_NER() exceeds self.chunk_size in length.
        
        Args:
            - def__get_NER (function): An alias intended for self.get_NER().

        Returns:
            function: The return value.

        Raises:
            - TypeError: If @text passed to self.get_NER() is not a string.
        """

        def processor(self, text):

            # prepare output container.
            ner_output = []
            
            # verify that @text is a string.
            if not isinstance(text, str):
                self.logger.error("Argument @text must be a string, got: {}".format(
                    type(text).__name__))
                self.logger.warning("Falling back to empty output.")
                return []

            # verify @text is not empty.
            if len(text) == 0:
                self.logger.warning("Argument @text was empty.")
                self.logger.warning("Falling back to empty output.")
                return []

            # if needed, break @text into smaller chunks.
            if len(text) <= self.chunk_size:
                text_list = [text]
            else:
                self.logger.info("Text exceeds chunk size of: {}".format(self.chunk_size))
                try:
                    wrapper = TextWrapper(width=self.chunk_size, break_long_words=False, 
                        break_on_hyphens=False, drop_whitespace=False, 
                        replace_whitespace=False)
                    text_list = wrapper.wrap(text)
                except Exception as err:
                    self.logger.error(err)
                    self.logger.error("Failed to chunk text.")
                    self.logger.warning("Falling back to empty output.")
                    return []

            # get NER tags for each item in @text_list.
            i = 1
            total_chunks = len(text_list)
            
            for text_chunk in text_list:
                self.logger.info("Getting NER tags for chunk {} of {}.".format(i, 
                    total_chunks))
                try:
                    tokenized_tagged = def__get_NER(self, text_chunk)
                except Exception as err:
                    self.logger.error(err)
                    self.logger.error("Failed to get NER tags for chunk.")
                    self.logger.warning("Falling back to empty output for chunk.")
                    tokenized_tagged = []
                
                # if @tokenized_tagged is not empty, append it to @ner_output.
                # if needed, also append orphaned whitespace before/after.
                if len(tokenized_tagged) != 0:

                    leading_space, trailing_space = self._get_outer_space(text_chunk)
                    
                    if leading_space != "":
                        ner_output += [("", "", leading_space)]
                    
                    ner_output += tokenized_tagged
                    
                    if trailing_space != "":
                        ner_output += [("", "", trailing_space)]
                    
                i += 1

            return ner_output

        return processor


    @__process_NER_requests
    def get_NER(self, text):
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
                if tag in self.tags_to_remove:
                    tag = ""

                # if @tag is from Stanford, add null pattern plus .edu authority domain.
                if tag in self.stanford_tags:
                    tag = "::stanford.edu::" + tag

                # append final values to @ner_output.
                token_group = text, tag, tspace
                ner_output.append(token_group)

        return ner_output


if __name__ == "__main__":
    pass


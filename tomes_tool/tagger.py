#!/usr/bin/env python3

""" This module contains a class to convert an EAXS file to a tagged EAXS document in which
message content has been run through an NLP application. The message and NER entities are
encoded in a defined schema. """

# import modules.
import sys; sys.path.append("..")
import logging
import logging.config
import os
import requests
import sys
import yaml
from tomes_tool.lib.eaxs_to_tagged import EAXSToTagged
from tomes_tool.lib.html_to_text import HTMLToText, ModifyHTML
from tomes_tool.lib.nlp_to_xml import NLPToXML
from tomes_tool.lib.text_to_nlp import TextToNLP


class Tagger():
    """ A class to convert an EAXS file to a tagged EAXS document.

    Example:
        >>> # write tagged EAXS version of EAXS file.
        >>> tagger = TOMESToolTagger(host="http://localhost:9003")
        >>> tagger.eaxs_tagger("sample_eaxs.xml") # outputs "sample_eaxs__tagged.xml".
        >>> tagger.eaxs_tagger("sample_eaxs.xml", "out.xml") # outputs "out.xml".
    """
    

    def __init__(self, host, check_host=False, charset="UTF-8"): 
        """ Sets instance attributes.
        
        Args:
            - host (str): The URL for the CoreNLP server (ex: "http://localhost:9003").
            - check_host (bool): Use True to automatically run self.ping_host(). Otherwise, 
            use False.
            - charset (str): Optional encoding for tagged EAXS.
        """
    
        # set logging.
        self.logger = logging.getLogger(__name__)        
        self.logger.addHandler(logging.NullHandler())

        # suppress third party logging that is not a warning or higher.
        # per: https://stackoverflow.com/a/11029841
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        # set attributes.
        self.host = host
        self.check_host = check_host
        self.charset = charset

        # if specified, verify @host is active before creating instances of modules.
        if self.check_host:
            self.ping_host()

        # compose instances.
        self.h2t = HTMLToText()
        self.t2n = TextToNLP(self.host)
        self.n2x = NLPToXML()
        self.e2t = EAXSToTagged(self.html_convertor, self.text_tagger, self.charset)


    def ping_host(self):
        """ Makes a test request to @self.host.
        
        Returns:
            None
            
        Raises:
            - ConnectionError: If a connection can't be made to @self.host.
        """

        self.logger.info("Testing if NLP server at '{}' exists.".format(self.host))
        try:
            requests.get(self.host)
            self.logger.info("Connection to server was successful.")
        except requests.exceptions.ConnectionError as err:
            self.logger.error(err)
            msg = "Can't connect to NLP server at: {}".format(self.host)
            self.logger.critical(msg)
            raise ConnectionError(msg)

        return


    def html_convertor(self, html):
        """ Converts @html string to a plain text.
        
        Args:
            - html (str): The HTML to convert.

        Returns:
            str: The return value.
        """

        # alter DOM.
        html = ModifyHTML(html)
        html.shift_links()
        html.remove_images()
        html = html.raw()
        
        # convert HTML to text.
        text = self.h2t.get_text(html, is_raw=True)
        return text


    def text_tagger(self, text):
        """ Converts plain @text to NLP-tagged, TOMES-specific XML.
        
        Args:
            - text (str): The text to convert to NLP-tagged XML.

        Returns:
            str: The return value.
        """

        # get NLP; convert to XML.
        nlp = self.t2n.get_NER(text)
        nlp = self.n2x.get_XML(nlp)
        return nlp

    
    def eaxs_tagger(self, eaxs_file, tagged_eaxs_file=None):
        """ Writes tagged version of @eaxs_file to @tagged_eaxs_file.
        
        Args:
            - eaxs_file (str): The EAXS file to convert.
            - tagged_eaxs_file (str): The tagged EAXS document will be written to this file.
            If None, this value will be @eaxs_file with the ".xml" extension replaced with
            "__tagged.xml".

        Returns:
            None

        Raises:
            Exception: If an exception was raised during the tagging process. Note: this does
            not ensure that the desired data was created, but only that no exceptions were
            raised.
        """

        self.logger.info("Attempting to tag EAXS file: {}".format(eaxs_file))
        
        # if needed, define output path.
        if tagged_eaxs_file is None:
            tagged_eaxs_file = eaxs_file.replace(".xml", "__tagged.xml")
        
        # create tagged EAXS.
        try:
            tagged = self.e2t.write_tagged(eaxs_file, tagged_eaxs_file)
        except Exception as err:
            err_name = type(err).__name__
            msg = ("{}: {}".format(err_name, err))
            self.logger.error(msg)
            raise Exception(msg)
        
        self.logger.info("Created tagged EAXS file: {}".format(tagged_eaxs_file))
        return


# CLI.
def main(eaxs: "source EAXS file", 
        output: ("tagged EAXS destination"),
        silent: ("disable console logs", "flag", "s"),
        host:("NLP server URL", "option")="http://localhost:9003"):

    "Converts EAXS document to tagged EAXS.\
    \nexample: `py -3 tagger.py ../tests/sample_files/sampleEAXS.xml tagged.xml`"

    # make sure logging directory exists.
    logdir = "log"
    if not os.path.isdir(logdir):
        os.mkdir(logdir)

    # get absolute path to logging config file.
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(config_dir, "logger.yaml")
    
    # load logging config file.
    with open(config_file) as cf:
        config = yaml.safe_load(cf.read())
    if silent:
        config["handlers"]["console"]["level"] = 100
    logging.config.dictConfig(config)
    
    # make tagged version of EAXS.
    try:
        tagger = Tagger(host, check_host=True)
        tagger.eaxs_tagger(eaxs, output)
        sys.exit()
    except Exception as err:
        sys.exit(err)


if __name__ == "__main__":
    
    import plac
    plac.call(main)


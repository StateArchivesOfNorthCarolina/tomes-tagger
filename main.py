#!/usr/bin/env python3

"""
This module contains a class to convert an EAXS file to a tagged EAXS documet in which
message content has been run through an NLP application. The message and NER entities are
encoded in a defined schema.

Todo:
    * What to do if NLP timeouts? You really need to write to file the message IDs of any 
    skipped messages due to timeouts or other errors.
        - This isn't a main() issue, but it's a high level concept nonetheless.
    * Need to be able to pass in CoreNLP server info from here.
        - Requires change to text_to_nlp.py.
"""

# import modules.
import logging
import logging.config
import os
import yaml
from lib.html_to_text import *
from lib.text_to_nlp import *
from lib.nlp_to_xml import *
from lib.eaxs_to_tagged import *


class TOMESToolTagger():
    """ A class to convert an EAXS file to a tagged EAXS document.

    Example:
        >>> # write tagged EAXS to "tagged.xml".
        >>> tagger = TOMESToolTagger()
        >>> tagger.eaxs_to_tagged(eaxs_file, "tagged.xml")
    """
    

    def __init__(self, charset="UTF-8"): 
        """ Sets instance attributes.
        
        Args:
            - charset (str): Optional encoding for tagged EAXS.
        """
    
        # set logging.
        self.logger = logging.getLogger(__name__)        

        # set attributes.
        self.charset = charset
        
        # compose instances.
        self.h2t = HTMLToText()
        self.t2n = TextToNLP()
        self.n2x = NLPToXML()
        self.e2t = EAXSToTagged(self.html_to_text, self.text_to_nlp, self.charset)


    def html_to_text(self, html):
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


    def text_to_nlp(self, text):
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

    
    def eaxs_to_tagged(self, eaxs_file, tagged_eaxs_file=None):
        """ Writes tagged version of @eaxs_file to @tagged_eaxs_file.
        
        Args:
            - eaxs_file (str): The EAXS file to convert.
            - tagged_eaxs_file (str): The tagged EAXS document will be written to this file.
            If None, this value will be @eaxs_file with the ".xml" extension replaced with
            "__tagged.xml".

        Returns:
            bool: The return value.
            True if the process completed. Otherwise, False.
        """

        self.logger.info("Attempting to tag EAXS file: {}".format(eaxs_file))

        # create tagged EAXS.
        if tagged_eaxs_file is None:
            tagged_eaxs_file = eaxs_file.replace(".xml", "__tagged.xml")
        try:
            tagged = self.e2t.write_tagged(eaxs_file, tagged_eaxs_file)
        except Exception as err:
            err_name = type(err).__name__
            self.logger.error("{}: {}".format(err_name, err))
            self.logger.warning("Can't tag EAXS file; aborting.")
            return False
        
        self.logger.info("Created tagged EAXS file: {}".format(tagged_eaxs_file))
        return True


# CLI.
def main(eaxs: "source EAXS file",
        output: ("tagged EAXS destination", "option", "o")):

    "Converts EAXS document to tagged EAXS.\
    \nexample: `py -3 main.py tests\sample_files\sampleEAXS.xml`"

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
    logging.config.dictConfig(config)
    
    # make tagged version of EAXS.
    tagger = TOMESToolTagger()
    tagger.eaxs_to_tagged(eaxs, output)


if __name__ == "__main__":
    
    import plac
    plac.call(main)


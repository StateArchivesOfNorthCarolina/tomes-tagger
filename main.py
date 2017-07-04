#!/usr/bin/env python3

"""
This module converts an EAXS file to a "tagged" version of the EAXS in which message content
has been run through an NLP application. The message and NER entities are encoded in a
defined schema.


TODO:
    - What to do if NLP timeouts? This is a lib.text_to_nlp issue.
    - Somebody needs to start the Stanford server: should it be this or text_to_nlp?
        - Probably the latter.
        - Well, if I do it here, then I can shut it down here, too via __exit__?
"""

# import modules.
from lib.html_to_text import *
from lib.text_to_nlp import *
from lib.nlp_to_xml import *
from lib.eaxs_to_tagged import *
#from lib.nlp_to_stats import * # Likely not going to be written.
#from lib.account_to_aip import * # Validate EAXS folder structure.
#from lib.folder_to_mets import * # METS creation seems out of scope for main.py.


class TOMESToolTagger():
    """ A class to convert an EAXS file to a "tagged" version of the EAXS in which message
    content has been run through an NLP application. The message and NER entities are encoded
    in a defined schema. """
    

    def __init__(self, charset="UTF-8"): 
        """ Sets instance attributes. """

        # set attributes.
        self.charset = charset
        
        # compose instances.
        self.h2t = HTMLToText()
        self.t2n = TextToNLP()
        self.n2x = NLPToXML()
        self.e2t = EAXSToTagged(self.html_to_text, self.text_to_nlpx, self.charset)


    def html_to_text(self, html):
        """ Converts HTML string (@html) to a plain text string.
        
        Args:
            - html (str): The HTML to convert.

        Returns:
            str: The return value.
        """

        h2t = self.h2t

        # alter DOM.
        html = ModifyHTML(html)
        html.shift_links()
        html.remove_images()
        html = html.raw()
        
        # convert HTML to text.
        text = h2t.text(html, is_raw=True)
        return text


    def text_to_nlpx(self, text):
        """ Converts plain text (@text) to a TOMES-specific XML version with NLP-tagged
        entities.
        
        Args:
            - text (str): The text to convert to NLP-tagged XML.

        Returns:
            str: The return value.
            The string is an XML document.
        """

        t2n = self.t2n
        n2x = self.n2x

        # get NLP; convert to XML.
        nlp = t2n.get_NLP(text)
        nlpx = n2x.xml(nlp, return_string=True)
        return nlpx


    def eaxs_to_tagged(self, eaxs_file, tagged_eaxs_file=None):
        """ Returns tagged version of @eaxs_file (str).
        
        Args:
            - eaxs_file (str): The EAXS file to convert.
            - tagged_eaxs_file (str): The tagged EAXS document will be written to this file.
            If None, this value will be @eaxs_file with the ".xml" extension replaced with
            "__tagged.xml".

        Returns:
            None
        """

        e2t = self.e2t
        
        # create tagged EAXS.
        if tagged_eaxs_file is None:
            tagged_eaxs_file = eaxs_file.replace(".xml", "__tagged.xml")
        tagged = e2t.write_tagged(eaxs_file, tagged_eaxs_file)
        
        return


# TEST.
def main(eaxs_file, tagged_eaxs_file=None):

    # make tagged version of EAXS.
    tagger = TOMESToolTagger()
    tagger.eaxs_to_tagged(eaxs_file, tagged_eaxs_file)


if __name__ == "__main__":
        
        import plac
        plac.call(main)


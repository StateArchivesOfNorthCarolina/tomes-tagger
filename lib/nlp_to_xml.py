#!/usr/bin/env python3

"""
This module converts Stanford CoreNLP JSON output to XML per the tagged EAXS schema.

Todo:
    * The XSD filename and object are static, so they should be in the __init__.
    * XSD won't validate if @xdoc has an XML declaration. Is there a way to fix that?
        - validate() should ONLY work for etree._Element and not strings. 
            - So, get rid of is_raw, etc.
            - Remember: you can't validate without an Internet connection, so handle that.
    * If jdict["sentences"] raises a TypeError, you need to handle it.
        - Or should you just raise and error before passing empty text to CoreNLP? That would
        certainly be more efficient.
        - You also need to log a warning.
"""

# import modules.
import codecs
import io
import json
import logging
from lxml import etree


class NLPToXML():
    """ A class for converting CoreNLP JSON output to XML per the tagged EAXS schema. """


    def __init__(self):
        """ Sets instance attributes. """

        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        
        # get XSD filepath.
        self.xsd_file = __file__.replace(".py", ".xsd")
        
        # set namespace attributes.
        self.ns_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {None: self.ns_uri}


    def _split_authority(self, auth_tag):
        """ Splits @auth_tag into the authority domain and NER tag.

        Args:
            - auth_tag (str): The forward-slash concatenated authority domain and NER tag.

        Returns:
            tuple: The return value.
            The first item is a string, i.e the authority domain.
            The second item is a string, i.e. the NER tag.
        """
        
        slash = auth_tag.find("/")

        # determine authority.
        if slash == -1:
            authority, ner_tag = "stanford.edu", auth_tag
        else:
            authority, ner_tag = auth_tag[0:slash], auth_tag[slash+1:]

        # if forward slashes are in @ner_tag, log a warning.
        if "/" in ner_tag:
            self.logger.warning("Forward slashes found in NER tag: {}".format(ner_tag))
        
        return (authority, ner_tag)


    def validate(self, xdoc, is_raw=True):
        """ Determines if XML document @xdoc is valid or not per the tagged EAXS
        schema.

        Args:
            - xdoc (str): The XML file OR the raw XML string to validate.
            - is_raw (bool): Use True for XML as string. Use False for an XML file.

        Returns:
            bool: The return value. True for valid, otherwise False.
        """
  
        # if @is_raw, make XML file-like.
        if is_raw:
            xdoc = io.StringIO(xdoc)
        
        # parse @xdoc and XSD.
        xdoc = etree.parse(xdoc)
        xsd = etree.parse(self.xsd_file)

        # validate @xdoc.
        validator = etree.XMLSchema(xsd)
        is_valid = validator.validate(xdoc)
        self.logger.debug("Tagged message XML validation yields: {}".format(is_valid))  

        return is_valid


    def xml(self, jdict):
        """ Converts CoreNLP JSON to lxml.etree._Element per the tagged EAXS schema for body
        content.
        
        Args:
            - jdict (dict): CoreNLP output to convert to XML.

        Returns:
            lxml.etree._Element: The return value.
        """

        # create root element.
        tagged_message = etree.Element("{" + self.ns_uri + "}TaggedContent",
                nsmap=self.ns_map)
        tagged_message.text = ""
        
        # start tracking NER tag groups with default authority/NER tag combination.
        tag_group = 0
        current_ner = ""

        # iterate through tokens; append sub-elements to root.
        sentences = jdict["sentences"]
        for sentence in sentences:
            
            tokens = sentence["tokens"]
            for token in tokens:
                
                # get required values.
                try:
                    originalText = token["originalText"]
                except KeyError:
                    originalText = token["word"]
                after = token["after"]
                ner = token["ner"]

                # if new tag, increase group value.
                if ner != current_ner and ner != "O":
                    current_ner = ner
                    tag_group += 1
            
                # create sub-element.
                tagged = etree.SubElement(tagged_message, "{" + self.ns_uri + "}Token",
                        nsmap=self.ns_map)
                
                # if NER tag exists, add attributes.
                if ner != "O":
                    tag_authority, tag_value = self._split_authority(ner)
                    tagged.set("entity", tag_value)
                    tagged.set("authority", tag_authority)
                    tagged.set("group", str(tag_group))
                
                # set text and append whitespace.
                tagged.text = originalText
                tagged.tail = after

        return tagged_message


    def xstring(self, jdict, charset="utf-8", header=True, beautify=False):
        """ Converts CoreNLP JSON to an XML string per the Tagged EAXS schema.

        Args:
            - jdict (dict): CoreNLP output to convert to XML.
            - charset (str): The encoding for the converted text.
            - header (bool): Use True to include an XML header in the output.
            - beautify (bool): Use True to pretty print.

        Returns:
            str: The return value.
        """

        # get tagged etree._Element.
        tagged_message = self.xml(jdict)

        # convert to string.
        tagged_message = etree.tostring(tagged_message, xml_declaration=header,
                encoding=charset, pretty_print=beautify)
        tagged_message = tagged_message.decode(charset)

        return tagged_message


if __name__ == "__main__":
    pass


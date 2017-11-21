#!/usr/bin/env python3

""" This module converts Stanford CoreNLP JSON output to XML per the tagged EAXS schema. """

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
        
        # get XSD filepath and parse XSD.
        self.xsd_file = __file__.replace(".py", ".xsd")
        self.xsd = etree.parse(self.xsd_file)
        
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


    def validate(self, xdoc):
        """ Determines if @xdoc is valid or not per the tagged EAXS schema file 
        @self.xsd_file.

        Args:
            - xdoc (str): The lxml.etree._Element to validate.

        Returns:
            bool: The return value. True for valid, otherwise False.
        """

        # validate @xdoc.
        validator = etree.XMLSchema(self.xsd)
        is_valid = validator.validate(xdoc)

        return is_valid


    def xml(self, jdict, validate=False):
        """ Converts CoreNLP JSON to lxml.etree._Element per the tagged EAXS schema for body
        content.
        
        Args:
            - jdict (dict): CoreNLP output to convert to XML.
            - validate (bool): If True, the resultant lxml.etree._Element will be validated 
            against @self.xsd_file. If False, no validation is attempted.

        Returns:
            lxml.etree._Element: The return value.
        """

        self.logger.info("Converting CoreNLP JSON to tagged EAXS schema.")

        # create root element.
        tagged_el = etree.Element("{" + self.ns_uri + "}Tokens",
                nsmap=self.ns_map)
        tagged_el.text = ""
        
        # start tracking NER tag groups with default authority/NER tag combination.
        tag_group = 0
        current_ner = ""

        # ensure CoreNLP JSON has required field.
        try:
            sentences = jdict["sentences"]
        except KeyError:
            self.logger.error("Required JSON field 'sentences' not found.")
            self.logger.debug("CoreNLP JSON: {}".format(jdict))

        # iterate through tokens; append sub-elements to root.
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
                token_el = etree.SubElement(tagged_el, "{" + self.ns_uri + "}Token",
                        nsmap=self.ns_map)
                
                # if NER tag exists, add attributes.
                if ner != "O":
                    tag_authority, tag_value = self._split_authority(ner)
                    token_el.set("entity", tag_value)
                    token_el.set("authority", tag_authority)
                    token_el.set("group", str(tag_group))
                
                # set text and append whitespace.
                token_el.text = originalText
                token_el.tail = after

        # if requested, validate tagged message.
        if validate:
            is_valid = self.validate(tagged_el) 
            if not is_valid:
                self.logger.warning("Tagged message XML is not valid per '{}'.".format(
                    self.xsd.file))

        return tagged_el


if __name__ == "__main__":
    pass


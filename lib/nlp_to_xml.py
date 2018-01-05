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

        # verify @auth_tag is a string.
        if not isinstance(auth_tag, str):
            self.logger.error("Authority should be a string, got '{}' instead.".format(
                type(auth_tag).__name__))
            self.logger.warning("Falling back to empty authority and NER tag values.")
            return ("", "")

        # determine authority.
        slash = auth_tag.find("/")
        
        if slash == -1:
            authority, ner_tag = "", auth_tag
        else:
            authority, ner_tag = auth_tag[0:slash], auth_tag[slash+1:]

        # if forward slashes are in @ner_tag, log a warning.
        if "/" in ner_tag:
            self.logger.warning("Forward slashes found in NER tag: {}".format(ner_tag))
        
        return (authority, ner_tag)


    def validate_xml(self, xdoc):
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


    def get_XML(self, ner_data, validate=False):
        """ Converts CoreNLP JSON to lxml.etree._Element per the tagged EAXS schema for body
        content.
        
        Args:
            - ner_data (list): The NER data to convert to XML. Each item in the list is 
            expected to be a tuple with three string values: a text token, its NER tag, and 
            its trailing space.
            - validate (bool): If True, the resultant lxml.etree._Element will be validated 
            against @self.xsd_file. If False, no validation is attempted.

        Returns:
            lxml.etree._Element: The return value.
        """

        self.logger.info("Converting NER list to a tagged XML message.")

        # create root element.
        tagged_el = etree.Element("{" + self.ns_uri + "}Tokens",
                nsmap=self.ns_map)
        tagged_el.text = ""
        
        # start tracking NER tag groups.
        tag_group = 0
        current_tag = None

        # verify that @ner_data is not empty.
        if len(ner_data) == 0:
            self.logger.warning("NER tag data is empty; XML output will be empty as well.")

        # iterate through @ner_data; append sub-elements to root.
        for token_group in ner_data:

            # verify that @token_group is a tuple.
            if not isinstance(token_group, tuple):
                self.logger.error("Token group is not a tuple; got {} instead.".format(
                    type(token_group).__name__))
                self.logger.warning("Skipping token group.")
                continue
            
            # verify that tuple's length is correct.
            if len(token_group) != 3:
                self.logger.error("Token group contains {} items, not 3.".format(
                    len(token_group)))
                self.logger.warning("Skipping token group.")
                continue

            # unpack tuple, and write to @tagged_el.
            try:
                text, tag, tspace = token_group
            except ValueError as err:
                self.logger.error(err)
                self.logger.warning("Skipping token group.")
                continue

            # add whitespace-only items to tree and continue.
            if text == "":
            
                # append space to previous child; otherwise fall back to new element.
                children = tagged_el.getchildren()
                if len(children) != 0:
                    children[-1].tail += tspace
                else:
                    block_el = etree.SubElement(tagged_el, "{" + self.ns_uri + "}BlockText", 
                            nsmap=self.ns_map)
                    block_el.text = tspace
                continue

            # if @tag is new, set new @current_tag value and increase group value.
            if tag != current_tag:
                current_tag = tag
                if tag != "":
                    tag_group += 1
        
            # create sub-element for token.
            token_el = etree.SubElement(tagged_el, "{" + self.ns_uri + "}Token",
                    nsmap=self.ns_map)
            
            # if NER tag exists, add attributes to token sub-element.
            if tag != "":

                tag_authority, tag_value = self._split_authority(tag)
                
                token_el.set("entity", tag_value)
                token_el.set("group", str(tag_group))

                # write attribute if it exists.
                if tag_authority != "": 
                    token_el.set("authority", tag_authority)
            
            # set token sub-element's text value and append whitespace.
            token_el.text = text
            token_el.tail = tspace

        # if requested, validate tagged message.
        if validate:
            is_valid = self.validate_xml(tagged_el) 
            if not is_valid:
                self.logger.warning("Tagged message XML is not valid per '{}'.".format(
                    self.xsd.file))

        return tagged_el


if __name__ == "__main__":
    pass


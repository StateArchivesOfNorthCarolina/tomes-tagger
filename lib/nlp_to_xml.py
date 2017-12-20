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


    def get_xml(self, ner_data, validate=False):
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

        self.logger.info("Converting NER list to an XML 'tagged' message.")

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
            
            text, tag, tspace = token_group

            # add pure whitespace to tree and continue.
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
                token_el.set("authority", tag_authority)
                token_el.set("group", str(tag_group))
            
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

    from text_to_nlp import *
    logging.basicConfig(level=logging.DEBUG)
    
    t2n = TextToNLP(port=9003)
    n2x = NLPToXML()

    #s = "Jack Jill\n\t\rpail"
    #s = "\nJack and Jill \t\t\t\t\t\tSingh went up a hill in:   North Carolina.\r"
    #s = " \n\n\t\t\r\r" + s
    #s = "Free Sony DVD"
    with open("MikeWard__choke_message.txt") as f:
        s = f.read()
    res = t2n.get_ner(s)
    #for i in res: print(i)
    xml = n2x.get_xml(res)
    xml = etree.tostring(xml).decode()
    print(xml)



#!/usr/bin/env python3

"""
This module converts Stanford CoreNLP JSON output to XML per the tagged EAXS schema.

Todo:
    * You need an external, canonical data source for the custom NER tags, perhaps a SKOS
    file.
        - Or at least make it optional in __init__.
        - Yes: the constructor should set the tag authories. This should be a list. It's the
        job of the user to obtain the list and pass it.
        - You also need them to pass in the default authority, otherwise it will be
        "ncdcr.gov".
    * The XSD filename and object are static, so they should be in the __init__.
    * XSD won't validate if @xdoc has an XML declaration. Is there a way to fix that?
    * validate() should ONLY work for etree._Element and not strings. 
        - So, get rid of is_raw.
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
        self.ns_uri = "http://archives.ncdcr.gov/mail-account/tagged-message/"
        self.ns_map  = {None: self.ns_uri}

        # set custom NER tags.
        self.custom_ner = ["GOV.state_agency",
                          "PII.bank_account_number",
                          "PII.beacon_id",
                          "PII.credit_card_number",
                          "PII.email_address",
                          "PII.employee_identification_number",
                          "PII.nc_drivers_license_number",
                          "PII.passport_number",
                          "PII.personal_health_information",
                          "PII.sensitive_document",
                          "PII.social_security_number"]


    def _get_authority(self, ner_tag):
        """ Gets the authority domain for an @ner_tag.

        Args:
            - ner_tag (str): The NER tag for which to get the authority.

        Returns:
            str: The return value.
        """

        if ner_tag in self.custom_ner:
            authority = "ncdcr.gov"
        else:
            authority = "stanford.edu"
        
        return authority


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
        """ Converts CoreNLP JSON to lxml.etree._Element per the tagged EAXS schema.
        
        Args:
            - jdict (dict): CoreNLP output to convert to XML.

        Returns:
            lxml.etree._Element: The return value.
        """

        # create root element.
        tagged_message = etree.Element("{" + self.ns_uri + "}tagged_message",
                nsmap=self.ns_map)
        tagged_message.text = ""
        
        # start tracking "tag" sub-elements.
        tag_id = 0
        current_tag = ""

        # add text or "tag" sub-element to root XML as needed.
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
                ner_tag = token["ner"]

                # if no NER tag found, append to root element and continue.
                # otherwise, add a "tag" sub-element.

                if ner_tag == "O":
                    current_tag = ner_tag
                    try:
                        tagged_message[-1].tail += originalText + after
                    except TypeError: # no previous tail.
                        tagged_message[-1].tail = originalText + after
                    except IndexError: # no child elements.
                        tagged_message.text += originalText + after
                    continue

                # if new tag value, increase "id" attribute value.
                if ner_tag != current_tag:
                    current_tag = ner_tag
                    tag_id += 1
                
                # get "authority" attribute value.
                tag_authority = self._get_authority(ner_tag)
            
                # add "tag" sub-element and attributes to root.
                tagged = etree.SubElement(tagged_message, "{" + self.ns_uri + "}tagged",
                        nsmap=self.ns_map)
                tagged.set("entity", ner_tag)
                tagged.set("authority", tag_authority)
                tagged.set("id", str(tag_id))
                tagged.text = originalText
                tagged.tail = after

        return tagged_message


    def xstring(self, jdict, charset="utf-8", header=True, beautify=True):
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


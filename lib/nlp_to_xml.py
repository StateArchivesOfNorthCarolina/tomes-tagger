#!/usr/bin/env python3

"""
This module converts Stanford CoreNLP JSON output to XML per the ./tagged_content.xsd schema.

TODO:
    -   Need an external, canonical data source for the custom NER tags, perhaps a SKOS file.
    -   XSD won't validate if @xdoc has an XML declaration. Is there a way to fix that?
    -   I want xml() to be less verbose. So, move the namespace stuff into _init__() and
        maybe use a private method to figure out the tag authority value.
    -   Use better variable names than (x_tokens, etc.) for xml(). They're ugly.
    
"""

# import modules.
import codecs
import io
import json
from lxml import etree

class NLPToXML():
    """ """

    def __init__(self):
        """ Sets attributes. """

        # custom NER tags.
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

        # "tagged_content" XSD file.
        self.XSD = "nlp_to_xml.xsd"


    def merge(self, jdocs, are_raw=True):
        """ """
        # needs to combine multiple Stanford JSON files for when signature and
        # non-signature portions of an email need to be merged after NER is run
        # only on the non-signature part.
        # @jdocs = list of JSON files or list of JSON strings (@are_raw == True).
        pass


    def validate(self, xdoc, is_raw=True, return_verbose=False):

        # if @is_raw, make XML file-like.
        if is_raw:
            xdoc = io.StringIO(xdoc)
        
        #
        xdoc = etree.parse(xdoc)

        #
        xsd = etree.parse(self.XSD)
        xsd = etree.XMLSchema(xsd)

        #
        if return_verbose:
            valid = xsd.assertValid(xdoc)
        else:
            valid = xsd.validate(xdoc)
        return valid


    def xml(self, jdict, charset="utf-8", return_string=True, header=False, beautify=True):
        """ """

        # create XML namespace.
        ns_url = "http://archives.ncdcr.gov/mail-account/tagged-content/"
        ns_prefix = "{" + ns_url + "}"
        ns_map = {None : ns_url}

        # create root element.
        x_tokens = etree.Element(ns_prefix + "tagged_content", nsmap=ns_map)
        x_tokens.text = ""
        
        #
        tag_id = 0
        current_tag = ""

        #
        sentences = jdict["sentences"] 
        for sentence in sentences:

            tokens = sentence["tokens"]
            for token in tokens:
                
                #
                try:
                    originalText = token["originalText"]
                except KeyError:
                    originalText = token["word"]
                after = token["after"]
                ner_tag = token["ner"]

                #
                if ner_tag == "O":
                    current_tag = ner_tag
                    try:
                        x_tokens[-1].tail += originalText + after
                    except TypeError: # no previous tail.
                        x_tokens[-1].tail = originalText + after
                    except IndexError: # no child elements.
                        x_tokens.text += originalText + after
                    continue
                
                # else ...

                #
                if ner_tag != current_tag:
                    current_tag = ner_tag
                    tag_id += 1

                #
                if ner_tag in self.custom_ner:
                    tag_authority = "ncdcr.gov"
                else:
                    tag_authority = "stanford.edu"
                
                #
                x_token = etree.SubElement(x_tokens, ns_prefix + "tagged", nsmap=ns_map)
                x_token.set("entity", ner_tag)
                x_token.set("authority", tag_authority)
                x_token.set("id", str(tag_id)   )
                x_token.text = originalText
                x_token.tail = after

        #
        if return_string:
            x_tokens = etree.tostring(x_tokens, xml_declaration=header, encoding=charset,
                                     pretty_print=beautify)
            x_tokens = x_tokens.decode(charset)
        return x_tokens


# TEST.
def main():
    n2x = NLPToXML()
    j = open("../tests/sample_files/sample_NER.json").read()
    j = json.loads(j)
    x = n2x.xml(j, return_string=True)
    valx = n2x.validate(x, is_raw=True, return_verbose=False)
    print (x, valx)

if __name__ == "__main__":
    main()

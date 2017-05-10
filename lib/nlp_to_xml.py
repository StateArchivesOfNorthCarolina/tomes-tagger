#!/usr/bin/env python3

"""
This module converts Stanford CoreNLP JSON output to XML per the ./tagged_content.xsd schema.

TODO:
    - Need an external, canonical data source for the custom NER tags, perhaps a SKOS file.
"""

# import modules.
import codecs
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


    def merge(self, jdocs, are_raw=True):
        """ """
        # needs to combine multiple Stanford JSON files for when signature and
        # non-signature portions of an email need to be merged after NER is run
        # only on the non-signature part.
        # @jdocs = list of JSON files or list of JSON strings (@are_raw == True).
        pass


    def xml(self, jdoc, is_raw=True, charset="utf-8", return_string=True, beautify=True):
        """ """

        # if @is_raw == False, read JSON file.
        if not is_raw:
            with codecs.open(jdoc, "r", encoding=charset) as tmp:
                jdoc = tmp.read()

        # load JSON.
        jsml = json.loads(jdoc)
        
        # create XML namespace.
        ns_url = "http://archives.ncdcr.gov/mail-account/tagged-content/"
        ns_prefix = "{" + ns_url + "}"
        ns_map = {None : ns_url}

        # create root element.
        x_tokens = etree.Element(ns_prefix + "tagged_content", nsmap=ns_map)
        x_tokens.text = ""
        
        # parse JSON; write XML.
        sentences = jsml["sentences"]
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
                    try:
                        x_tokens[-1].tail += originalText + after
                    except TypeError: # no previous tail.
                        x_tokens[-1].tail = originalText + after
                    except IndexError: # no child elements.
                        x_tokens.text += originalText + after
                    continue
                
                #
                if ner_tag in self.custom_ner:
                    tag_authority = "ncdcr.gov"
                else:
                    tag_authority = "stanford.edu"
                
                #
                x_token = etree.SubElement(x_tokens, ns_prefix + "tagged", nsmap=ns_map)
                x_token.set("entity", ner_tag)
                x_token.set("authority", tag_authority)
                x_token.text = originalText
                x_token.tail = after
        
        #
        if return_string:
            x_tokens = etree.tostring(x_tokens, pretty_print=beautify)
            x_tokens = x_tokens.decode(charset)
        return x_tokens


# TEST.
def main():
    n2x = NLPToXML()
    x = n2x.xml("../tests/sample_files/sample_NER.json", is_raw=False, return_string=True)
    return x

if __name__ == "__main__":
    x = main()
    print(x)

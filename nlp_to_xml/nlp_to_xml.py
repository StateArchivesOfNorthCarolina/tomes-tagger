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

class JsonToXML():
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


    def xml(self, jdoc, is_raw=False, charset="utf-8", as_string=True, beautify=True):
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
        x_tokens = etree.Element(ns_prefix + "tokens", nsmap=ns_map)
        
        # parse JSON; write XML.
        sentences = jsml["sentences"]
        for sentence in sentences:
        
            tokens = sentence["tokens"]
            for token in tokens:
                
                #
                originalText = token["originalText"]
                ner = token["ner"]
                after = token["after"]
                
                #
                x_token = etree.SubElement(x_tokens, ns_prefix + "token", nsmap=ns_map)
                x_token.text = originalText
                x_token.set("suffix", after)
    
                # 
                if ner != "O":
 
                    if ner in self.custom_ner:
                        authority = "ncdcr.gov"
                    else:
                        authority = "stanford.edu"

                    x_token.set("NER", ner)
                    x_token.set("NER.authority", authority)
                
        #
        if as_string:
            x_tokens = etree.tostring(x_tokens, pretty_print=beautify)
            x_tokens = x_tokens.decode(charset)
        return x_tokens


# TEST.
def main():
    j2x = JsonToXML()
    x = j2x.xml("sample.json", as_string=True)
    return x

if __name__ == "__main__":
    x = main()
    print(x)

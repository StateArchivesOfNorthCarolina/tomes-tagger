#!/usr/bin/env python3

"""
This module converts Stanford CoreNLP JSON output to XML per the ./tagged_content.xsd schema.

TODO:
    - You need an external, canonical data source for the custom NER tags, perhaps a SKOS
    file.
        - Or at least make it optional in __init__.
        - Yes: the constructor should set the tag authories.
    - The XSD filename and object are static, so they should be in the __init__.
    - XSD won't validate if @xdoc has an XML declaration. Is there a way to fix that?
        - Just set a validation option in xml() and validate BEFORE adding the header, etc.
        - If you do this, you need to return a tuple (xml doc, True|False|None
        (None = not validated)). Then, also make validate() a private method.
    - If jdict["sentences"] raises a TypeError, you need to handle it.
        - Or should you just make not to pass empty text to CoreNLP?
"""

# import modules.
import codecs
import io
import json
from lxml import etree


class NLPToXML():
    """ A class for converting CoreNLP JSON output to XML per the ./tagged_content.xsd
    schema. """

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


    def get_authority(self, ner_tag):
        """ Returns the authority's domain for an NER tag.

        Args:
            - ner_tag (str): The NER tag for which to get the authority.

        Returns:
            <class 'str'>
        """

        if ner_tag in self.custom_ner:
            tag_authority = "ncdcr.gov"
        else:
            tag_authority = "stanford.edu"
        
        return tag_authority


    def validate(self, xdoc, is_raw=True):
        """ Determines if XML document @xdoc is valid or not per the ./tagged_content.xsd
        schema.

        Args:
            - xdoc (str): The XML file OR the raw XML string to validate.
            - is_raw (bool): Use True for XML as string. Use False for an XML file.

        Returns:
            <class 'bool'>
        """
  
        # if @is_raw, make XML file-like.
        if is_raw:
            xdoc = io.StringIO(xdoc)
        
        # parse @xdoc and XSD.
        xdoc = etree.parse(xdoc)
        xsd = __file__.replace(".py", ".xsd")
        xsd = etree.parse(xsd)

        # validate @xdoc.
        xsd = etree.XMLSchema(xsd)
        valid = xsd.validate(xdoc)

        return valid


    def xml(self, jdict, charset="utf-8", return_string=True, header=False, beautify=True):
        """ Converts CoreNLP JSON to XML per the ./tagged_content.xsd schema.
        
        Args:
            - jdict (dict): CoreNLP output to convert to XML.
            - charset (str): The encoding for the converted text.
            - return_string (bool): Use True to return an XML string. Use False to return an
            lxml.etree._Element.
            - header (bool): Use True to include an XML header in the output. Use False to
            omit the header.
            - beautify (bool): Use True to pretty print the return value if @return_string is
            True.

        Returns:
            <class 'str'>: If @return_string is True.
            <class 'lxml.etree._Element'>: If @return_string is False.
        """

        # create XML namespace map.
        ns_url = "http://archives.ncdcr.gov/mail-account/tagged-content/"
        ns_prefix = "{" + ns_url + "}"
        ns_map = {None : ns_url}

        # create root element.
        tagged_content = etree.Element(ns_prefix + "tagged_content", nsmap=ns_map)
        tagged_content.text = ""
        
        # start tracking "tag" subelements.
        tag_id = 0
        current_tag = ""

        # add text or "tag" subelements to root as needed.
        sentences = jdict["sentences"] 
        for sentence in sentences:
            
            tokens = sentence["tokens"]
            for token in tokens:
                
                # get important key values.
                try:
                    originalText = token["originalText"]
                except KeyError:
                    originalText = token["word"]
                after = token["after"]
                ner_tag = token["ner"]

                # if no NER tag, add to root element and continue;
                # otherwise, add a "tag" sub-element.
                if ner_tag == "O":
                    current_tag = ner_tag
                    try:
                        tagged_content[-1].tail += originalText + after
                    except TypeError: # no previous tail.
                        tagged_content[-1].tail = originalText + after
                    except IndexError: # no child elements.
                        tagged_content.text += originalText + after
                    continue

                # add a "tag" sub-element.
                
                # if new tag value, increase "id" attribute value.
                if ner_tag != current_tag:
                    current_tag = ner_tag
                    tag_id += 1
                
                # get "authority" attribute value.
                tag_authority = self.get_authority(ner_tag)
            
                # add "tag" subelement and attributes to root.
                tagged = etree.SubElement(tagged_content, ns_prefix + "tagged", nsmap=ns_map)
                tagged.set("entity", ner_tag)
                tagged.set("authority", tag_authority)
                tagged.set("id", str(tag_id)   )
                tagged.text = originalText
                tagged.tail = after

        # convert output to string if needed.
        if return_string:
            tagged_content = etree.tostring(tagged_content, xml_declaration=header,
                            encoding=charset, pretty_print=beautify)
            tagged_content = tagged_content.decode(charset)

        return tagged_content


# TEST.
def main(json_file):

    # load JSON.
    jdoc = open(json_file).read()
    jdict = json.loads(jdoc)

    # convert JSON to XML and validate XML.
    n2x = NLPToXML()
    xdoc = n2x.xml(jdict, return_string=True)
    valid = n2x.validate(xdoc, is_raw=True)
    print(xdoc)
    print(valid)

if __name__ == "__main__":
    
    import plac
    plac.call(main)


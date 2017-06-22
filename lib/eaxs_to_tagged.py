#!/usr/bin/env python3

"""
This module has a class for ...

TODO:
    - Docstrings.
    - The XPath you have for BodyContent needs to only find BodyContent where
    ContentType = "text/html" or "text/plain".
        - IOW, you're relying on the textual content to be in first position.
    - Does the updated value for "Charset" need to be uppercase?
    - Is "TransferEncoding" a required element?
"""

# import modules.
import base64
from lxml import etree


class EAXSToTagged():
    """ A class for ... 
    
    Example:
    >>> eaxs = EAXSToTagged("sampleEAXS.xml" ...)
    """


    def __init__(self, eaxs_file, tagged_eaxs_file, html_stripper, nlp_tagger,
            charset="utf-8"):
        """ Sets instance attributes.
        
        Args:
            - eaxs_file (str): Path to EAXS file.
            - charset (str): Optional encoding with which to open @eaxs_file.
            ???
        """

        # set attributes.
        self.eaxs_file = eaxs_file
        self.tagged_eaxs_file = tagged_eaxs_file
        self.html_stripper = html_stripper
        self.nlp_tagger = nlp_tagger
        self.charset = charset
        
        # set namespace attributes.
        self.ncdcr_prefix = "ncdcr"
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {self.ncdcr_prefix:self.ncdcr_uri,
                "xsi":"http://www.w3.org/2001/XMLSchema-instance"}
    

    def _get_root(self):
        """ Gets root "Account" element ... """
        
        pass

    
    def _get_globalID(self):
        """ """
        
        pass
    

    def _get_folders(self):
        """ Gets all <Folder> elements in self.eaxs_file. 
        
        Returns:
            <class 'lxml.etree.iterparse'>
        """
        
        eaxs_file = self.eaxs_file
        ncdcr_uri = self.ncdcr_uri
        
        # get element generator. 
        folder_el = "{" + ncdcr_uri + "}Folder"
        folders = etree.iterparse(eaxs_file, events=("end",), tag=folder_el,
                strip_cdata=False)
        
        return folders

    
    def _get_messages(self, folder):
        """ Gets all <Message> elements from an EAXS <Folder> element. 
        
        Args:
            - folder (lxml.etree._Element): An EAXS <Folder> etree element.

        Returns:
            <class 'lxml.etree.ElementChildIterator'>
        """
        
        ncdcr_uri = self.ncdcr_uri
        
        # get element generator.
        message_el = "{" + ncdcr_uri + "}Message"
        messages =  folder.iterchildren(tag=message_el)
        
        return messages


    def _update_message(self, message):
        """
        
        Args:
            - message (lxml.etree._Element):
        """

        tagged_eaxs_file = self.eaxs_file
        ncdcr_prefix = self.ncdcr_prefix
        ns_map = self.ns_map
        html_stripper = self.html_stripper
        nlp_tagger = self.nlp_tagger
        charset = self.charset

        # re-usable path prefix. 
        _singleBody = "ncdcr:MultiBody/ncdcr:SingleBody[1]/"

        # elements to alter.
        #message_id = message.xpath("ncdcr:MessageId/text()", namespaces=ns_map)
        charset_el = message.xpath(_singleBody + "ncdcr:Charset[1]", namespaces=ns_map)[0]
        content_el = message.xpath(_singleBody + "ncdcr:BodyContent/ncdcr:Content[1]",
                namespaces=ns_map)[0]
        content_type_el = message.xpath(_singleBody + "ncdcr:ContentType[1]",
                namespaces=ns_map)[0]
        transfer_encoding_el = message.xpath(_singleBody + "ncdcr:TransferEncoding[1]",
                namespaces=ns_map)

        # stop if no content.
        if content_el != None:
            if content_el.text == None:
                return message

        # decode Base64 if needed.
        if len(transfer_encoding_el) != 0:
            transfer_encoding_el = transfer_encoding_el[0]
            if transfer_encoding_el.text == "base64":
                text = base64.b64decode(content_el.text)
                content_el.text = text.decode(encoding=charset, errors="backslashreplace")
        
        # alter element values.
        charset_el.text = charset
        if content_type_el.text == "text/html":
            content_el.text = html_stripper(content_el.text)
        content_el.text = nlp_tagger(content_el.text)
        content_type_el.text = "text/xml"
        transfer_encoding_el = None
        
        return message


    def tag_eaxs(self):
        """ """

        pass


# TEST.
def main(eaxs_file, tagged_eaxs_file):

    e2t = EAXSToTagged(eaxs_file, tagged_eaxs_file,  lambda x: x, lambda x: "FOOBAR")
    folders = e2t._get_folders()
    for event, folder in folders:
        messages = e2t._get_messages(folder)
        for message in messages:
            messagex = e2t._update_message(message)
            messagex = etree.tostring(messagex, pretty_print=True)
            messagex = messagex.decode()
            print(messagex)
            break
        folder.clear()


if __name__ == "__main__":
        
        import plac
        plac.call(main)


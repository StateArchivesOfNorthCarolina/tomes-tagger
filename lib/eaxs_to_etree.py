#!/usr/bin/env python3

"""
This module has a class to parse an EAXS file's message content with lxml.

TODO:
    - The XPath you have for BodyContent needs to only find BodyContent where ContentType = "text/html" or "text/plain".
        - IOW, by using etree.find() you're relying on the textual content to be in first position.
"""

# import modules.
from lxml import etree


class EAXSToEtree():
    """ A class for manipulating an EAXS file's message content. 
    
    Example:
    >>> eaxs = EAXSToEtree("sampleEAXS.xml")
    >>> message_dict = eaxs.messages() # get message elements.
    >>> for key, value in message_dict.items():
    >>>   print(key) # dictionary key for element
    >>>   print(value) # lxml.etree._Element or None
    >>>   if value is not None: 
    >>>     value.text = "Hello world!"  
    >>> eaxs = eaxs.to_etree() # EAXS as lxml.etree
    >>> etree.tostring(eaxs) # string version of EAXS
    """


    def __init__(self, eaxs_file, charset="utf-8"):
        """ Sets instance attributes.
        
        Args:
            - eaxs_file (str): Path to EAXS file.
            - charset (str): Optional encoding with which to open @eaxs_file.
        """

        # set args.
        self.eaxs_file = eaxs_file 
        self.charset = charset
        
        # set namespace for EAXS.
        self.ncdcr_ns = {"ncdcr": "http://www.archives.ncdcr.gov/mail-account"}


    def _get_messages(self):
        """ Gets all messages in EAXS document. 
        
        Returns:
            <class 'list'>
        """
        
        # set root, namespace to use.
        root = self.to_etree()
        ncdcr_ns = self.ncdcr_ns
        
        # get and return message elements.
        messages = root.findall("ncdcr:Folder/ncdcr:Message", ncdcr_ns)
        return messages


    def _get_message_elements(self, message):
        """ Gets important message elements.
        
        Args:
            - message (lxml.etree._Element): The EAXS message element from which to find given
            subelements.

        Returns:
            <class 'dict'>
        """

        # namespace to use.
        ncdcr_ns = self.ncdcr_ns

        # given elements to retrieve via XPath. 
        _singleBody = "ncdcr:MultiBody/ncdcr:SingleBody/"

        message_id = message.find("ncdcr:MessageId", ncdcr_ns)
        charset = message.find(_singleBody + "ncdcr:Charset", ncdcr_ns)
        content = message.find(_singleBody + "ncdcr:BodyContent/ncdcr:Content", ncdcr_ns)
        content_type = message.find(_singleBody + "ncdcr:ContentType", ncdcr_ns)
        transfer_encoding = message.find(_singleBody + "ncdcr:TransferEncoding", ncdcr_ns)
        
        # set and return dictionary.
        message_dict = {"message_id":message_id,
                        "charset":charset,
                        "content":content,
                        "content_type":content_type,
                        "transfer_encoding":transfer_encoding}
        return message_dict


    def messages(self):
        """ Returns list of dictionaries. Each dictionary pertains to a single message and
        contains a given set of message elements.

        Returns:
            <class 'list'>
        """

        # local shortcuts to class methods.
        messages = self._get_messages()
        get_message_elements = self._get_message_elements
        
        # set and return list of message elements. 
        messages = [get_message_elements(message) for message in messages]
        return messages


    def to_etree(self):
        """ Gets root element for EAXS file.
        
        Returns:
            <class 'lxml.etree._Element'>
        """

        # EAXS file to parse.
        eaxs_file = self.eaxs_file
        
        # parse file; leaving CData intact.
        parser = etree.XMLParser(strip_cdata=False)
        with open(eaxs_file, "rb") as eaxs:
            tree = etree.parse(eaxs, parser=parser)
        
        # return root.
        root = tree.getroot()
        return root


# TEST.
def main(eaxs_file):

    eaxs = EAXSToEtree(eaxs_file)
    message = eaxs.messages()[0]
    for key, value in message.items():
        print(key, ": ", value)
    
if __name__ == "__main__":
        
        import plac
        plac.call(main)


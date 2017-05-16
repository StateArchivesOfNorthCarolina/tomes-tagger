#!/usr/bin/env python3

"""
This module has a class to parse an EAXS file's message content with lxml."

TODO:
    - The XPath you have for BodyContent needs to only find BodyContent where ContentType = "text/html" or "text/plain".
        - IOW, by using etree.find() you're relying on the textual content to be in first position.
"""

# import modules.
from lxml import etree


class EAXSToEtree():
    """ A class for parsing an EAXS file's message content with lxml. 
    
    Example:
    >>> eaxs = EAXSToEtree("sampleEAXS.xml")
    >>> message_dict = eaxs.messages() # get message elements.
    >>> for key, value in message_dict.items():
    >>>   print(key) # dictionary key for element.
    >>>   print(value) # lxml.etree element or None.
    """


    def __init__(self, eaxs_file, charset="utf-8"):
        """ Sets instance attributes.
        
        Args:
            - eaxs_file (string): Path to EAXS file.
            - charset (string): Optional encoding with which to open @eaxs_file.
        """

        # set args.
        self.eaxs_file = eaxs_file 
        self.charset = charset
        
        # set namespace for EAXS.
        self.ncdcr_ns = {"ncdcr": "http://www.archives.ncdcr.gov/mail-account"}
        
        # get/set root element for @self.eaxs_file.
        self.root = self._get_root()


    def _get_root(self):
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
        
        # get and return root.
        root = tree.getroot()
        return root


    def _get_message_elements(self, message):
        """ Gets important message elements.
        
        Returns:
            <class 'dict'>
        """

        # namespace to use.
        ncdcr_ns = self.ncdcr_ns

        # given elements to retrieve via XPath.
        _path = "ncdcr:MultiBody/ncdcr:SingleBody/"
        charset = message.find(_path + "ncdcr:Charset", ncdcr_ns)
        content = message.find(_path + "ncdcr:BodyContent/ncdcr:Content", ncdcr_ns)
        content_type = message.find(_path + "ncdcr:ContentType", ncdcr_ns)
        transfer_encoding = message.find(_path + "ncdcr:MultiBody/ncdcr:SingleBody/ncdcr:BodyContent/ncdcr:TransferEncoding", ncdcr_ns)
        
        # set and return dictionary.
        message_dict = {"charset":charset,
                        "content":content,
                        "content_type":content_type,
                        "transfer_encoding":transfer_encoding}
        return message_dict

    
    def _get_messages(self):
        """ Gets all messages in EAXS document. 
        
        Returns:
            <class 'list'>
        """
        
        # set root, namespace to use.
        root = self.root
        ncdcr_ns = self.ncdcr_ns
        
        # get and return message elements.
        messages = root.findall("ncdcr:Folder/ncdcr:Message", ncdcr_ns)
        return messages


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


# TEST.
def main():

    import sys
    
    try:
        f = sys.argv[1]
    except:
        exit("Please pass an EAXS file via the command line.")
    
    eaxs = EAXSToEtree(f)
    mdata = eaxs.messages()[0]
    for k,v in mdata.items():
        print(k, ": ", v)
        print(type(v))
    
if __name__ == "__main__":
	main()


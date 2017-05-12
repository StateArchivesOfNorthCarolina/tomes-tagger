#!/usr/bin/env python3

"""
Parses EAXS for easy access to messages.

TODO:
    - The XPath you have for BodyContent needs to only find BodyContent where ContentType = "text/html" or "text/plain".
        - IOW, by using etree.find() you're relying on the textual content to be in first position.
"""

# import modules.
from lxml import etree

class EAXSToEtree():

    def __init__(self, eaxs_file, charset="utf-8"):
        """ """

        self.eaxs_file = eaxs_file 
        self.charset = charset
        self.ncdcr_ns = {"ncdcr": "http://www.archives.ncdcr.gov/mail-account"}
        self.root = self.get_root()


    def get_root(self):
        """ """

        eaxs_file = self.eaxs_file
        
        # parse EAXS; leaving CData intact.
        parser = etree.XMLParser(strip_cdata=False)

        with open(eaxs_file, "rb") as eaxs:
            tree = etree.parse(eaxs, parser=parser)
        
        root = tree.getroot()
        return root


    def get_message_elements(self, message):
        """ """

        #
        ncdcr_ns = self.ncdcr_ns

        #
        content = message.find("ncdcr:MultiBody/ncdcr:SingleBody/ncdcr:BodyContent/ncdcr:Content", ncdcr_ns)
        content_type = message.find("ncdcr:MultiBody/ncdcr:SingleBody/ncdcr:ContentType", ncdcr_ns)
        transfer_encoding = message.find("ncdcr:MultiBody/ncdcr:SingleBody/ncdcr:BodyContent/ncdcr:TransferEncoding", ncdcr_ns)

        return (content, content_type, transfer_encoding)

    
    def get_messages(self):
        """ """
        
        #
        root = self.root
        ncdcr_ns = self.ncdcr_ns
        
        #
        messages = root.findall("ncdcr:Folder/ncdcr:Message", ncdcr_ns)

        return messages


    def messages(self):
        """ """

        #
        messages = self.get_messages()
        get_message_elements = self.get_message_elements
        
        #
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
    content, content_type, transfer_encoding = eaxs.messages()[0]
    print(content)
    print(content_type)
    print(transfer_encoding)
    
if __name__ == "__main__":
	main()

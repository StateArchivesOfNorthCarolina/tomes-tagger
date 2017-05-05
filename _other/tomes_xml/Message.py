#!/usr/bin/python

"""
TO DO:
    - add script docstring and state that an existing ElementTree.Element is required for use.
    - should "Namespace: http://www.history.ncdcr.gov/SHRAB/ar/EmailPreservation/mail-account/mail-account_single.xsd" be default @namespace value in __init__?
    - replace use of find_rec() with in-line call to etree's findall().
    - replace use of get_header with in-line code.
        - i.e. 'self.ret_path = self.headers.get("Return-Path")'
    - verify docstring for set_sentence_vectors() is correct (i.e. do you know what it's doing?)
"""

class MessageBlock(object):
    """Creates a Message object from an XML document.
    Conforms to XML Schema for a Single E-Mail Account XSD.

    XSD: http://www.history.ncdcr.gov/SHRAB/ar/EmailPreservation/mail-account/mail-account.xsd
    Namespace: http://www.history.ncdcr.gov/SHRAB/ar/EmailPreservation/mail-account/mail-account_single.xsd
    """

    def __init__(self, msg, namespace):
        """Creates @msg Message object with a given XML @namespace.
        
        Keyword arguments:
        
        @type msg xml.etree.ElementTree.Element
        @type namespace str
        """

        # set attributes.
        self.msg = msg
        self.namespace = namespace
        self.sentence_vectors = []
        self.headers = self.package_headers()
        
        # get XML elements; set attributes.
        try:
            self.message_id = self.get_item(self.namespace+"MessageId")
            self.orig_date = self.get_item(self.namespace+"OrigDate")
            self.from_id = self.get_item(self.namespace+"From")
            self.to_id = self.get_item(self.namespace+"To")
            self.ret_path = self.get_header("Return-Path")
            self.content = self.package_msg()
        except AttributeError:
            return
        finally:
            self.msg = None

    @staticmethod
    def find_rec(node, element):
        """Returns list of all occurrences of @element for a given @node.
        
        Keyword arguments:
        
        @type node xml.etree.ElementTree.Element
        @type element str
        """
        
        recs = node.findall(".//"+element)
        return recs

    def get_header(self, ids):
        """ Returns value from Message object's "headers" dictionary for a given key, @ids.
        
        Keyword arguments:
        
        @type ids str
        """
        
        item = None
        item = self.headers.get(ids)
        return item

    def get_item(self, req):
        """Returns value of first element @req from Message object.

        Keyword arguments:
        
        @type req str
        """

        item = None
        try:
            item = self.msg.find(req).text # value of first occurence of element.
        except AttributeError:
            pass
        return item

    def package_headers(self):
        """Returns dictionary with Message object's Header Value if Header Name = "Return-Path"."""
        
        headers = {}
        for elem in self.msg.findall(self.namespace+"Header"):
            if elem.find(self.namespace+"Name").text == "Return-Path":
                try:
                    headers["Return-Path"] = elem.find(self.namespace+"Value").text
                except AttributeError:
                    continue
        return headers

    def package_msg(self):
        """Returns list of values from Message object's Content elements if ContentType = "text/plain"."""
        
        contents = []
        messages = self.find_rec(self.msg, self.namespace+"SingleBody")
        for message in messages:
            if message.find(self.namespace+"ContentType").text == "text/plain":
                content = self.find_rec(message, self.namespace+"Content")
                try:
                    contents.append(content[0].text)
                except IndexError:
                    pass
        return contents

    def set_sentence_vector(self, sent, ratio):
        """Appends (@sent, @ratio) tuple to Message object's "sentence_vectors" list.
        
        Keyword arguments:
        
        @type sent str???
        @type ratio float???
        """
        
        vector = (sent, ratio)
        self.sentence_vectors.append(vector)
        return

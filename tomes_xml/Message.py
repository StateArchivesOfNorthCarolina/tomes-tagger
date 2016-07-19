import logging


class MessageBlock:
    def __init__(self, msg, namespace):
        """Create a Message object from an xml document conforming to the XML Schema for a Single E-Mail Account XSD.
        Namespace: http://www.history.ncdcr.gov/SHRAB/ar/EmailPreservation/mail-account/mail-account_single.xsd

        Keyword arguments:

        @type msg xml.etree.ElementTree.Element
        @type namespace str
        """
        self.msg = msg
        self.sentence_vectors = []
        self.namespace = namespace
        self.headers = self.package_headers()
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

    def get_item(self, req):
        """Return an element value from the original message

        Keyword arguments:
            @type req str

            Should have the form

        """
        item = None
        try:
            item = self.msg.find(req).text
        except AttributeError:
            pass
        return item

    def package_headers(self):
        headers = {}
        for elem in self.msg.findall(self.namespace+"Header"):
            if elem.find(self.namespace+"Name").text == "Return-Path":
                try:
                    headers["Return-Path"] = elem.find(self.namespace+"Value").text
                except AttributeError:
                    continue
        return headers

    def get_header(self, ids):
        item = None
        item = self.headers.get(ids)
        return item

    def package_msg(self):
        contents = []
        msg = self.find_rec(self.msg, self.namespace+"SingleBody")
        for n in msg:
            if n.find(self.namespace+"ContentType").text == "text/plain":
                content = self.find_rec(n, self.namespace+"Content")
                try:
                    contents.append(content[0].text)
                except IndexError:
                    pass
        return contents

    def set_sentence_vector(self, sent, ratio):
        self.sentence_vectors.append((sent, ratio))

    @staticmethod
    def find_rec(node, element):
        """
            @type node xml.etree.ElementTree.Element
            @type element str
        :return:
        """
        return node.findall(".//"+element)
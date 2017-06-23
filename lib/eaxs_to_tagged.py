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
    - Parse and alter the elements in the order they appear in the schema. It's just logical.
    - Need to check if Charset is None, because per the XSD that means "text/plain" is
    assumed.
    - Should you pass the "Charset" to the NLP tagged even though Stanford doesn't seem to
    care? Ideally yes, so you can easily pass a different NLP tagger to this class.
    -  >>> content_text = content_text.decode(charset, errors="backslashreplace")
    #"ignore" works too. Which is better?
"""

# import modules.
import base64
from lxml import etree
    

class EAXSToTagged():
    """ A class for ... 
    
    Example:
    >>> eaxs = EAXSToTagged("sampleEAXS.xml" ...)
    """


    def __init__(self, eaxs_file, tagged_eaxs_file, strip_html, nlp_tagger,
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
        self.strip_html = strip_html
        self.nlp_tagger = nlp_tagger
        self.charset = charset
        
        # set namespace attributes.
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {"ncdcr":self.ncdcr_uri,
                "xsi":"http://www.w3.org/2001/XMLSchema-instance"}

        # re-usable path prefix. 
        self.singleBody = "ncdcr:MultiBody/ncdcr:SingleBody[1]/"

    
    def _get_messages(self, folder_el):
        """ Gets all <Message> elements from an EAXS <Folder> element. 
        
        Args:
            - folder_el (lxml.etree._Element): An EAXS <Folder> etree element.

        Returns:
            <class 'lxml.etree.ElementChildIterator'>
        """
        
        ncdcr_uri = self.ncdcr_uri
        
        # get element generator.
        message_el = "{" + ncdcr_uri + "}Message"
        messages =  folder_el.iterchildren(tag=message_el)
        
        return messages


    def _get_element(self, message_el, el_name, default_value=None):
        """ """

        ns_map, singleBody = self.ns_map, self.singleBody
        
        el_path = "ncdcr:BodyContent/ncdcr:{}[1]".format(el_name)
        elems = message_el.xpath(singleBody + el_path, namespaces=ns_map)
        
        el, el_text = None, default_value
        if len(elems) > 0:
            el, el_text = elems[0], elems[0].text
        
        return (el, el_text)


    def _update_message(self, message_el):
        """
        
        Args:
            - message_el (lxml.etree._Element):
        """

        tagged_eaxs_file = self.eaxs_file
        ns_map = self.ns_map
        strip_html = self.strip_html
        nlp_tagger = self.nlp_tagger
        charset = self.charset

        # elements to alter.
        print(message_el.xpath("ncdcr:MessageId/text()", namespaces=self.ns_map)) # test line.

        content_el, content_text = self._get_element(message_el, "Content") 
        charset_el, charset_text = self._get_element(message_el, "Content", "us-ascii")
        content_type_el, content_type_text = self._get_element(message_el, "ContentType",
                "text/plain")
        transfer_encoding_el, transfer_encoding_text = self._get_element(message_el, "Content")

        # stop if no content.
        if content_el is None or content_text is None:
            return message_el

        # decode Base64 if needed.
        if transfer_encoding_text == "base64":
            content_text = base64.b64decode(content_text)
            content_text = content_text.decode(charset, errors="backslashreplace")
            content_text = etree.CDATA(content_text)

        # alter element values.
        if charset_el is not None:
            charset_el.text = charset        
        if content_type_text == "text/html":
            content_text = strip_html(content_text)
        content_el.text = nlp_tagger(content_text)
        transfer_encoding_el = None
        
        return message_el


    def tag_eaxs(self):
        """ Writes file ... return filepath ... """

        eaxs_file = self.eaxs_file
        ncdcr_uri = self.ncdcr_uri

        #
        account = "{" + ncdcr_uri + "}Account"
        account_el = etree.Element(account)

        #
        root = etree.iterparse(eaxs_file, tag=account, strip_cdata=False)
        root = next(root)[1]
        
        children = root.iterchildren()
        for child_el in children:
            if child_el.tag == "{" + ncdcr_uri + "}Folder":
                messages = self._get_messages(child_el)
                for message_el in messages:
                    message_el = self._update_message(message_el)
            account_el.append(child_el)

        return account_el


# TEST.
def main(eaxs_file, tagged_eaxs_file):

    e2t = EAXSToTagged(eaxs_file, tagged_eaxs_file,  lambda x: x, lambda x: "FOOBAR")
    tagged = e2t.tag_eaxs()
    print(tagged)
    with open("foo.xml", "w") as f:
        f.write(etree.tostring(tagged, pretty_print=True).decode())


if __name__ == "__main__":
        
        import plac
        plac.call(main)


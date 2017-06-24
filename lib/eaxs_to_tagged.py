#!/usr/bin/env python3

"""
This module has a class for ...

TODO:
    - Docstrings.
    - Add to_file() method? Or just have tag_eaxs() write to file? Maybe an option (to string
    OR to file)?
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
    - It's odd: just editing the EAXS in place gets me a nicer output re: pretty printing.
    Using iterparse to get the root and appending the children to a new "Account" root
    element gets me odd looking output. Until we need to deal with massive EAXS files, I'll
    leave it as is for now.
"""

# import modules.
import base64
from lxml import etree
    

class EAXSToTagged():
    """ A class for ... 
    
    Example:
    >>> eaxs = EAXSToTagged("sampleEAXS.xml" ...)
    """


    def __init__(self, strip_html, nlp_tagger, charset="utf-8"):
        """ Sets instance attributes.
        
        Args:
            - charset (str): Optional encoding with which to open @eaxs_file.
            ???
        """

        # set attributes.
        self.strip_html = strip_html
        self.nlp_tagger = nlp_tagger
        self.charset = charset
        
        # set namespace attributes.
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {None:self.ncdcr_uri,
                "xsi":"http://www.w3.org/2001/XMLSchema-instance"}

    
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


    def _get_element(self, message_el, tag, value=None):
        """ """

        ncdcr_uri = "{" + self.ncdcr_uri + "}"
    
        el_path = "{ncdcr_uri}MultiBody/{ncdcr_uri}SingleBody[1]/"
        el_path += "{ncdcr_uri}BodyContent/{ncdcr_uri}{tag}[1]"
        el_path = el_path.format(ncdcr_uri=ncdcr_uri, tag=tag)

        elems = message_el.find(el_path)
        
        el, el_text = None, value
        if elems is not None:
            el, el_text = elems, elems.text
        
        return (el, el_text)


    def _update_message(self, message_el):
        """
        
        Args:
            - message_el (lxml.etree._Element):
        """

        strip_html = self.strip_html
        nlp_tagger = self.nlp_tagger
        charset = self.charset

        # elements to alter.
        content_el, content_text = self._get_element(message_el, "Content") 
        charset_el, charset_text = self._get_element(message_el, "Charset", "us-ascii")
        content_type_el, content_type_text = self._get_element(message_el, "ContentType",
                "text/plain")
        transfer_encoding_el, transfer_encoding_text = self._get_element(message_el,
                "TransferEncoding")

        # stop if no content.
        if content_el is None or content_text is None:
            return message_el

        # decode Base64 if needed.
        if transfer_encoding_text == "base64":
            content_text = base64.b64decode(content_text)
            content_text = content_text.decode(charset, errors="backslashreplace")

        # alter element values.
        if charset_el is not None:
            charset_el.text = charset        
        if content_type_text == "text/html":
            content_text = strip_html(content_text)
        content_text = nlp_tagger(content_text)
        content_el.text = etree.CDATA(content_text)
        transfer_encoding_el = None
        
        return message_el


    def get_tagged(self, eaxs_file):
        """ Writes file ... return filepath ... """

        ncdcr_uri = self.ncdcr_uri

        # 
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(eaxs_file, parser).getroot()

        #
        children = root.iterchildren()
        for child_el in children:
            if child_el.tag == "{" + ncdcr_uri + "}Folder":
                messages = self._get_messages(child_el)
                for message_el in messages:
                    message_el = self._update_message(message_el)

        return root


    def write_tagged(self, eaxs_file, tagged_eaxs_file=None):
        """ """
        
        charset = self.charset        
        
        if tagged_eaxs_file is None:
            tagged_eaxs_file = eaxs_file.replace(".xml", "__tagged.xml")
        
        tagged_root = self.get_tagged(eaxs_file)
        with etree.xmlfile(tagged_eaxs_file, encoding=charset) as xf:
            xf.write_declaration()
            xf.write(tagged_root, pretty_print=True)
        

# TEST.
def main(eaxs_file):

    e2t = EAXSToTagged(lambda x: x, lambda x: "FOOBAR")
    tagged = e2t.write_tagged(eaxs_file, "testTagged.xml")


if __name__ == "__main__":
        
        import plac
        plac.call(main)


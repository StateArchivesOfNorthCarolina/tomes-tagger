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
    Using iterparse, iterchildren gets me odd looking output. Until we need to deal with
    massive EAXS files, I'll leave it as is for now.
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
    
        bodyContent = "{ncdcr_uri}MultiBody/{ncdcr_uri}SingleBody[1]/"
        bodyContent += "{ncdcr_uri}BodyContent/{ncdcr_uri}{tag}[1]"
        
        el_path = bodyContent.format(ncdcr_uri=ncdcr_uri, tag=tag)
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

        tagged_eaxs_file = self.eaxs_file
        ns_map = self.ns_map
        strip_html = self.strip_html
        nlp_tagger = self.nlp_tagger
        charset = self.charset

        # elements to alter.
        content_el, content_text = self._get_element(message_el, "Content") 
        charset_el, charset_text = self._get_element(message_el, "Content", "us-ascii")
        content_type_el, content_type_text = self._get_element(message_el, "ContentType",
                "text/plain")
        transfer_encoding_el, transfer_encoding_text = self._get_element(message_el,
                "Content")

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


    def tag_eaxs(self):
        """ Writes file ... return filepath ... """

        eaxs_file = self.eaxs_file
        ncdcr_uri = self.ncdcr_uri
        ns_map = self.ns_map

        #
        account = "{" + ncdcr_uri + "}Account"
        account_el = etree.Element(account, nsmap=ns_map)

        # 
        parser = etree.XMLParser(strip_cdata=False, collect_ids=False)
        root = etree.parse(eaxs_file, parser).getroot()

        #
        children = root.getchildren()#iterchildren()
        for child_el in children:
            if child_el.tag == "{" + ncdcr_uri + "}Folder":
                messages = self._get_messages(child_el)
                for message_el in messages:
                    message_el = self._update_message(message_el)
            
        return root


# TEST.
def main(eaxs_file, tagged_eaxs_file):

    e2t = EAXSToTagged(eaxs_file, tagged_eaxs_file,  lambda x: x, lambda x: "FOOBAR")
    tagged = e2t.tag_eaxs()

    with etree.xmlfile("foo.xml", encoding="UTF-8") as f:
        f.write_declaration()
        f.write(tagged, pretty_print=True)

if __name__ == "__main__":
        
        import plac
        plac.call(main)


#!/usr/bin/env python3

"""
This module has a class for converting an EAXS file to a tagged EAXS document as either an
lxml.etree_Element or an XML file.

TODO:
    - The XPath you have for BodyContent needs to only find BodyContent where
    ContentType = "text/html" or "text/plain" or whatever is required to skip attachments.
        - see <MessageId><![CDATA[<7D5283D6710CD94BB9271326E415C3720FB0B2@email.nccrimecontrol.org>]]></MessageId>
        - IOW, you're relying on the textual content to be in first position.
"""

# import modules.
import base64
import os
from lxml import etree
    

class EAXSToTagged():
    """ A class for converting an EAXS file to a tagged EAXS document as either an
    lxml.etree_Element or an XML file.

    Example:
        >>> fake_html2text = lambda x: "" # convert HTML to plain text.
        >>> fake_text2nlp = lambda x: ""  # convert plain text to NLP output.
        >>> e2t = EAXSToTagged(fake_html2text, fake_text2nlp) # EAXS to tagged EAXS instance.
        >>> #tagged = e2t.get_tagged(eaxs_file) # tagged EAXS as lxml.etree._Element.
        >>> tagged = e2t.write_tagged(eaxs_file, "output.xml") # tagged EAXS to file.
    """


    def __init__(self, html_converter, nlp_tagger, charset="UTF-8"):
        """ Sets instance attributes.
        
        Args:
            
            - html_converter (function): Any function that accepts HTML text (str) as its
            only required argument and returns a plain text version (str).
            
            - nlp_tagger (function): Any function that accepts plain text (str) as its only
            required argument and returns an NLP tagged version (str).
            
            - charset (str): Optional encoding with which to update EAXS message content.
            This is also the encoding used to write a tagged EAXS file with the
            write_tagged() method.
        """

        # set attributes.
        self.html_converter = html_converter
        self.nlp_tagger = nlp_tagger
        self.charset = charset
        
        # set namespace attributes.
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {None:self.ncdcr_uri,
                "xsi":"http://www.w3.org/2001/XMLSchema-instance"}

    
    def _get_messages(self, folder_el):
        """ Gets all <Message> elements for a given <Folder> element. 
        
        Args:
            - folder_el (lxml.etree._Element): An EAXS <Folder> element.

        Returns:
            lxml.etree.ElementChildIterator: The return value.
            Each item within the iterator is an lxml.etree._Element.
        """
        
        ncdcr_uri = self.ncdcr_uri
        
        # get element generator.
        message_el = "{" + ncdcr_uri + "}Message"
        messages =  folder_el.iterchildren(tag=message_el)
 
        return messages


    def _get_element(self, message_el, name, value=None):
        """ Gets <Message/MultiBody/SingleBody[1]/@name> element and its text value.
        
        Args:
            - message_el (lxml.etree._Element): An EAXS <Message> element.
            - name (str): The element to retrieve.
            - value (str): An optional default text value for @name.

        Returns:
            tuple: The return value.
            The first item is an lxml.etree.Element, i.e. the element @name.
            The second item is a str, i.e. @name's value.
        """

        ncdcr_uri = "{" + self.ncdcr_uri + "}"
    
        # set XPath to @name.
        name = name.replace("/", "/{ncdcr_uri}").format(ncdcr_uri=ncdcr_uri)
        path = "{ncdcr_uri}MultiBody/{ncdcr_uri}SingleBody[1]/{ncdcr_uri}{name}[1]"
        path = path.format(ncdcr_uri=ncdcr_uri, name=name)

        # get element.
        name_el = message_el.find(path)
        
        # assume defaults; replace with actual values if element exists.
        el, el_text = None, value
        if name_el is not None:
            el, el_text = name_el, name_el.text

        return (el, el_text)


    def _update_message(self, message_el):
        """ Replaces the <BodyContent/Content> for a given <Message/MultiBody/SingleBody[1]>
        element.
        
        Args:
            - message_el (lxml.etree._Element): The <Message> element to be updated.

        Returns:
            lxml.etree._Element: The return value.
            The updated <Message> element.
        """

        html_converter = self.html_converter
        nlp_tagger = self.nlp_tagger
        charset = self.charset
        get_element = self._get_element

        # get needed element.
        content_el, content_text = get_element(message_el, "BodyContent/Content")
        transfer_encoding_el, transfer_encoding_text = get_element(message_el,
                "TransferEncoding")
        content_type_el, content_type_text = get_element(message_el, "ContentType",
                "text/plain")
         
        # stop if no <Content> element exists.
        if content_el is None or content_text is None:
            return message_el

        # decode Base64 <Content> if needed.
        if transfer_encoding_text == "base64":
            content_text = base64.b64decode(content_text)
            content_text = content_text.decode(charset, errors="backslashreplace")

        # alter <Content>; wrap in CDATA block.
        if content_type_text in ["text/html", "application/xml+html"]:
            content_text = html_converter(content_text)
        content_text = nlp_tagger(content_text)
        content_el.text = etree.CDATA(content_text)
        
        return message_el


    def get_tagged(self, eaxs_file):
        """ Converts an @eaxs_file to a tagged EAXS document.
        
        Args:
            - eaxs_file (str): The filepath for the EAXS file to convert.

        Returns:
            lxml.etree._Element: The return value.
            The tagged EAXS document.
        """

        ncdcr_uri = self.ncdcr_uri
        get_messages = self._get_messages
        update_message = self._update_message

        # parse @eaxs_file; set root.
        parser = etree.XMLParser(strip_cdata=False)
        root = etree.parse(eaxs_file, parser).getroot()

        # iterate through elements; update <Message> elements. 
        children = root.iterchildren()
        for child_el in children:
            if child_el.tag == "{" + ncdcr_uri + "}Folder":
                messages = get_messages(child_el)
                for message_el in messages:
                    message_el = update_message(message_el)

        return root


    def write_tagged(self, eaxs_file, tagged_eaxs_file):
        """ Converts an EAXS file to a tagged EAXS document and writes it to
        @tagged_eaxs_file.
        
        Args:    
            - eaxs_file (str): The filepath for the EAXS file to convert.
            - tagged_eaxs_file (str): The filepath that the tagged EAXS document will be
            written to.

        Returns:
            None

        Raises:
            - FileExistsError: If @tagged_eaxs_file already exists.
        """

        charset = self.charset
        get_tagged = self.get_tagged

        # raise error if output file already exists.
        if os.path.isfile(tagged_eaxs_file):
            err = "{} already exists.".format(tagged_eaxs_file)
            raise FileExistsError(err)
        
        # write tagged EAXS document to file.
        tagged_root = get_tagged(eaxs_file)
        with etree.xmlfile(tagged_eaxs_file, encoding=charset) as xf:
            xf.write_declaration()
            xf.write(tagged_root, pretty_print=True)

        return
        

# TEST.
def main(eaxs_file):

    def mark(s):
        if s[:5] == "Text > NLP":
            return "HTML > NLP" # HTML conversion was run.
        else:
            return "Text > NLP" # HTML conversion was not run.
    e2t = EAXSToTagged(mark, mark)
    tagged = e2t.write_tagged(eaxs_file, "testTagged.xml")


if __name__ == "__main__":
        
        import plac
        plac.call(main)


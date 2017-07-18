#!/usr/bin/env python3

"""
This module contains a class for converting an EAXS file to a tagged EAXS document as either
an lxml.etree_Element or an XML file.

Todo:
    * Do you need to support <ExtBodyContent> messages?
    * Add valid() method. Should be able to check etree._Element OR XML file.
"""

# import modules.
import base64
import logging
import os
from lxml import etree
    

class EAXSToTagged():
    """ A class for converting an EAXS file to a tagged EAXS document.

    Example:
        >>> html2text = def html2text(html) ... # convert HTML to plain text.
        >>> text2nlp = def text2nlp(text) ... # convert plain text to NLP-tagged output.
        >>> e2t = EAXSToTagged(html2text, text2nlp)
        >>> #tagged = e2t.get_tagged(eaxs_file) # tagged EAXS as lxml.etree._Element.
        >>> tagged = e2t.write_tagged(eaxs_file, "tagged.xml") # tagged EAXS to "tagged.xml".
    """


    def __init__(self, html_converter, nlp_tagger, charset="UTF-8"):
        """ Sets instance attributes.
        
        Args:
            - html_converter (function): Any function that accepts HTML text (str) as its
            only required argument and returns a plain text version (str).
            - nlp_tagger (function): Any function that accepts plain text (str) as its only
            required argument and returns an NLP-tagged version (str).
            - charset (str): Encoding with which to update EAXS message content.
            This is also the encoding used to write a tagged EAXS file with the
            write_tagged() method.
        """

        # suppress logging by default. 
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        
        # set attributes.
        self.html_converter = html_converter
        self.nlp_tagger = nlp_tagger
        self.charset = charset
        
        # set namespace attributes.
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {"ncdcr":self.ncdcr_uri,
                "xsi":"http://www.w3.org/2001/XMLSchema-instance"}

    
    def _get_messages(self, folder_el):
        """ Gets all <Message> elements for a given <Folder> element. 
        
        Args:
            - folder_el (lxml.etree._Element): An EAXS <Folder> element.

        Returns:
            lxml.etree.ElementChildIterator: The return value.
            Each item within the iterator is an lxml.etree._Element.
        """
        
        # get element generator.
        message_el = "{" + self.ncdcr_uri + "}Message"
        messages =  folder_el.iterchildren(tag=message_el)
 
        return messages

    
    def _get_message_id(self, message_el):
        """ Gets the message's <MessageId> value. 
        
        Args:
            message_el (lxml.etree._Element): The <Message> element from which to get the
            <MessageId>.
        
        Returns:
            str: The return value.
            The message identifier.
        """

        # get identifier value; strip whitespace.
        path = "ncdcr:MessageId"
        message_id = message_el.xpath(path, namespaces=self.ns_map)[0].text
        message_id = message_id.strip()
 
        return message_id


    def _get_element(self, message_el, name, value=None):
        """ Gets <Message/MultiBody/SingleBody/@name> element and its text value. Note that
        <SingleBody> elements for attachments are skipped.
        
        Args:
            - message_el (lxml.etree._Element): An EAXS <Message> element.
            - name (str): The element to retrieve.
            - value (str): The default text value for @name.

        Returns:
            tuple: The return value.
            The first item is an lxml.etree._Element, i.e. @name.
            The second item is a str, i.e. @name's value.
        """

        # set XPath to @name, omitting attachments.
        name = name.replace("/", "/ncdcr:")
        path = "ncdcr:MultiBody"
        path += "/ncdcr:SingleBody[(not(contains(ncdcr:Disposition, 'attachment')))][1]"
        path += "/ncdcr:{name}"
        path = path.format(name=name)

        # get element.
        name_el = message_el.xpath(path, namespaces=self.ns_map)
        
        # assume defaults; replace with actual values if element exists.
        el, el_text = None, value
        if len(name_el) > 0:
            name_el = name_el[0]
            el, el_text = name_el, name_el.text

        return (el, el_text)


    def _update_message(self, message_el):
        """ Replaces the <BodyContent/Content> for a given <Message/MultiBody/SingleBody>
        element. Note that <SingleBody> elements for attachments are skipped.
        
        Args:
            - message_el (lxml.etree._Element): The <Message> element to be updated.

        Returns:
            lxml.etree._Element: The return value.
            The updated <Message> element.
        """

        # get needed element.
        content_el, content_text = self._get_element(message_el, "BodyContent/Content")
        transfer_encoding_el, transfer_encoding_text = self._get_element(message_el,
                "TransferEncoding")
        content_type_el, content_type_text = self._get_element(message_el, "ContentType",
                "text/plain")
         
        # return <Message> if no <Content> sub-element exists.
        if content_el is None or content_text is None:
            return message_el

        # decode Base64 <Content> if needed.
        if transfer_encoding_text == "base64":
            content_text = base64.b64decode(content_text)
            content_text = content_text.decode(self.charset, errors="backslashreplace")

        # convert HTML to text if needed.
        if content_type_text in ["text/html", "application/xml+html"]:
            content_text = self.html_converter(content_text)
        
        # tag <Content>; wrap in CDATA block.
        content_text = self.nlp_tagger(content_text)
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

        # parse @eaxs_file; set root for tagged output.
        parser = etree.XMLParser(strip_cdata=False)
        tagged = etree.parse(eaxs_file, parser).getroot()

        # iterate through elements; update <Message> elements. 
        children = tagged.iterchildren()
        for child_el in children:
            if child_el.tag == "{" + self.ncdcr_uri + "}Folder":
                messages = self._get_messages(child_el)
                for message_el in messages:
                    message_id = self._get_message_id(message_el)
                    logging.info("Updating message: " + message_id)
                    message_el = self._update_message(message_el)

        return tagged


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

        # raise error if output file already exists.
        if os.path.isfile(tagged_eaxs_file):
            err = "{} already exists.".format(tagged_eaxs_file)
            raise FileExistsError(err)
        
        # write tagged EAXS document to file.
        tagged_root = self.get_tagged(eaxs_file)
        with etree.xmlfile(tagged_eaxs_file, encoding=self.charset) as xml:
            xml.write_declaration()
            xml.write(tagged_root, pretty_print=True)
            
        return
        

if __name__ == "__main__":
    pass


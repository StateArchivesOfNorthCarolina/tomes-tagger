#!/usr/bin/env python3

"""
This module has a class for converting an EAXS file to a tagged EAXS document as either an
lxml.etree_Element or an XML file.

TODO:
    - Docstrings.
    - The XPath you have for BodyContent needs to only find BodyContent where
    ContentType = "text/html" or "text/plain" or whatever is required to skip attachments.
        - see <MessageId><![CDATA[<7D5283D6710CD94BB9271326E415C3720FB0B2@email.nccrimecontrol.org>]]></MessageId>
        - IOW, you're relying on the textual content to be in first position.
    - Does the updated value for "Charset" need to be uppercase?
    - Is "TransferEncoding" a required element?
    - Parse and alter the elements in the order they appear in the schema. It's just logical.
        - Also change order in docstring for update_message().
    - Should you pass the "Charset" to the NLP tagged even though Stanford doesn't seem to
    care? Ideally yes, so you can easily pass a different NLP tagger to this class.
        - So add *args/**kwargs to text_to_nlp?
    -  >>> content_text = content_text.decode(charset, errors="backslashreplace")
    #"ignore" works too. Which is better?
    - If charset_el or content_type_el are None, you need to create the element and add it so
    that you can update the .text value.
"""

# import modules.
import base64
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


    def __init__(self, html_converter, nlp_tagger, charset="utf-8"):
        """ Sets instance attributes.
        
        Args:
            
            - html_converter (function): Any function that accepts HTML text (str) as its
            only required argument and returns plain text (str).
            
            - nlp_tagger (function): Any function that accepts plain text (str) as its only
            required argument and returns a string.
            
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
            <class 'lxml.etree.ElementChildIterator'>
        """
        
        ncdcr_uri = self.ncdcr_uri
        
        # get element generator.
        message_el = "{" + ncdcr_uri + "}Message"
        messages =  folder_el.iterchildren(tag=message_el)
 
        return messages


    def _get_element(self, message_el, name, value=None):
        """ Gets @tag sub-element and its text value for a given
        <Message/MultiBody/SingleBody[1]> element.
        
        Args:
            
            - message_el (lxml.etree._Element): An EAXS <Message> element.
            
            - name (str): The sub-element to retrieve.

            - value (str): An optional default text value for @name.

        Returns:
            <class 'tuple'>: (lxml.etree.Element, str)
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
        """ Replaces <BodyContent/Content>, <Charset>, <ContentType>, and
        <TransferEncoding> elements for a given <Message/MultiBody/SingleBody[1]> element.
        
        Args:
            - message_el (lxml.etree._Element): The <Message> element for which to alter the
            sub-elements mentioned above.

        Returns:
            <class 'lxml.etree._Element'>
        """

        html_converter = self.html_converter
        nlp_tagger = self.nlp_tagger
        charset = self.charset
        get_element = self._get_element

        # get elements.
        content_el, content_text = get_element(message_el, "BodyContent/Content") 
        charset_el, charset_text = get_element(message_el, "Charset", "us-ascii")
        content_type_el, content_type_text = get_element(message_el, "ContentType",
                "text/plain")
        transfer_encoding_el, transfer_encoding_text = get_element(message_el,
                "TransferEncoding")
        
        # stop if no <Content> element exists.
        if content_el is None or content_text is None:
            return message_el

        # decode Base64 if needed.
        if transfer_encoding_text == "base64":
            content_text = base64.b64decode(content_text)
            content_text = content_text.decode(charset, errors="backslashreplace")

        # alter each element.
        if content_type_text == "text/html":
            content_text = html_converter(content_text)
        content_text = nlp_tagger(content_text)
        content_el.text = etree.CDATA(content_text)
        
        if charset_el is not None:
            charset_el.text = charset
        
        if content_type_el is not None:
            content_type_el.text = "text/xml"
        
        transfer_encoding_el = None
        
        return message_el


    def get_tagged(self, eaxs_file):
        """ Converts an EAXS file to a tagged EAXS document.
        
        Args:
            - eaxs_file (str): The filepath for the EAXS file to convert to a tagged EAXS
            document.

        Returns:
            <class 'lxml.etree._Element'>
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


    def write_tagged(self, eaxs_file, tagged_eaxs_file=None):
        """ Converts an EAXS file to a tagged EAXS document and writes it to a file.
        
        Args:
            
            - eaxs_file (str): The filepath for the EAXS file to convert to a tagged EAXS
            document.

            - tagged_eaxs_file (str): The filepath that the tagged EAXS document will be
            written to.

        Returns:
            <class 'NoneType'>
        """

        charset = self.charset
        get_tagged = self.get_tagged
        
        # create output filename if needed.
        if tagged_eaxs_file is None:
            tagged_eaxs_file = eaxs_file.replace(".xml", "__tagged.xml")
        
        # get tagged EAXS document; write to file.
        tagged_root = get_tagged(eaxs_file)
        with etree.xmlfile(tagged_eaxs_file, encoding=charset) as xf:
            xf.write_declaration()
            xf.write(tagged_root, pretty_print=True)

        return
        

# TEST.
def main(eaxs_file):

    def mark(s):
        if s[:5] == "n2t()":
            return "h2t(); n2t()" # HTML conversion was run.
        else:
            return "n2t()" # HTML conversion was not run.
    e2t = EAXSToTagged(mark, mark)
    tagged = e2t.write_tagged(eaxs_file, "testTagged.xml")


if __name__ == "__main__":
        
        import plac
        plac.call(main)


#!/usr/bin/env python3

"""
This module contains a class for converting an EAXS file to a tagged EAXS document as either
an lxml.etree_Element or an XML file.

Todo:
    * Do you need to support <ExtBodyContent> messages?
        - I think "yes" and you'll need to append attributes/elements accordingly.
        - I think _update_message MIGHT be doing this already?
    * Do you really need huge_tree when iterparsing?
    * Dependning on fate of <Message/@Restricted, you might change "tagged_tree" to
    "tagged_content" to signify it's not an etree._Element but rather a string. Basically,
    I need a tree for detecting PII and otherwise just want a string.
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
        >>> text2nlp = def text2nlp(text) ... # convert plain text to NLP output.
        >>> e2t = EAXSToTagged(html2text, text2nlp)
        >>> tagged = e2t.write_tagged(eaxs_file, "output.xml") # tagged EAXS to "output.xml".
    """


    def __init__(self, html_converter, nlp_tagger, charset="UTF-8"):
        """ Sets instance attributes.

        Args:
            - html_converter (function): Any function that accepts HTML text (str) as its
            only required argument and returns a plain text version (str).
            - nlp_tagger (function): Any function that accepts plain text (str) as its only
            required argument and returns a tuple where the first item is an NLP-tagged
            XML message (str) and the second item (bool) is True if the text is believed to
            contain sensitive material.
            - charset (str): Encoding with which to update EAXS message content.
            This is also the encoding used to write a tagged EAXS file with the
            write_tagged() method.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.html_converter = html_converter
        self.nlp_tagger = nlp_tagger
        self.charset = charset

        # set namespace attributes.
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {"ncdcr":self.ncdcr_uri}


    def _get_message_id(self, message_el):
        """ Gets <Message/MessageId> value.

        Args:
            message_el (lxml.etree._Element): An EAXS <Message> element.

        Returns:
            str: The return value.
            The message identifier.
        """

        # get identifier value; strip whitespace.
        path = "ncdcr:MessageId"
        message_id = message_el.xpath(path, namespaces=self.ns_map)[0].text
        message_id = message_id.strip()

        return message_id


    def _get_single_body_element(self, message_el, name, value=""):
        """ Gets <Message/MultiBody/SingleBody/@name> element and its text value. Note that
        <SingleBody> elements for attachments are skipped.

        Args:
            - message_el (lxml.etree._Element): An EAXS <Message> element.
            - name (str): The element to retrieve.
            - value (str): The default text value for @name.

        Returns:
            tuple: The return value.
            The first item is an lxml.etree._Element, i.e. @name.
            The second item is a string, i.e. @name's value.
        """

        # set XPath for @name, omitting attachments.
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


    def _tag_message(self, message_el, content_text):
        """ ??? ... ???

        Args:
            - message_el (lxml.etree._Element): The <Message> element to be updated.
            - content_text (str): ???

        Returns:
            tuple: The return value.
            The first item is an lxml.etree._Element: the tagged XML tree.
            The second item is a string: the original message stripped of HTML tags and/or
            Base64-decoded. If the messages was unaltered, this value is None.
        """

        # ???
        transfer_encoding_el, transfer_encoding_text = self._get_single_body_element(
                message_el, "TransferEncoding")
        content_type_el, content_type_text = self._get_single_body_element(message_el,
                "ContentType")

        # ???
        is_stripped = False

        # decode Base64 <Content> if needed.
        if transfer_encoding_text.lower() == "base64":
            self.logger.info("Decoding Base64 message content.")
            content_text = base64.b64decode(content_text)
            content_text =  content_text.decode(self.charset, errors="backslashreplace")
            is_stripped = True

        # convert HTML to text if needed.
        if content_type_text.lower() in ["text/html", "application/xml+html"]:
            self.logger.info("Requesting HTML to plain text conversion.")
            content_text = self.html_converter(content_text)
            is_stripped = True

        # get NLP tags.
        self.logger.info("Requesting NLP tags.")
        tagged_tree = self.nlp_tagger(content_text)

        # ???
        stripped_content = None
        if is_stripped:
            stripped_content = content_text

        return (tagged_tree, stripped_content)


    def _update_message(self, message_el, folder_name):
        """ ???

        Args:
            - message_el (lxml.etree._Element): The <Message> element to be updated.
            - folder_name (str): The name of the EAXS <Folder> element containing <Message>
            element.

        Returns:
            lxml.etree._Element: The return value.
            The updated <Message> element.
        """
        
        # ???
        message_el.set("ParentFolder", folder_name)
        message_el.set("Processed", "false")
        message_el.set("Record", "true")
        ##message_el.set("Restricted", "false")
        message_el.append(etree.Element("Restriction", nsmap=self.ns_map))

        # get <Content>.
        content_el, content_text = self._get_single_body_element(message_el,
                        "BodyContent/Content")

        # if no <Content> sub-element exists, return <Message>.
        if content_el is None or content_text is None:
                return message_el

        # otherwise ...
        tagged_tree, stripped_content = self._tag_message(message_el, content_text)
        #tagged_tree = etree.tostring(tagged_tree, encoding=self.charset)

        # ???
        single_body_el = etree.Element("SingleBody", nsmap=self.ns_map)
        tagged_content_el = etree.Element("TaggedContent", nsmap=self.ns_map)
        tagged_content_el.text = etree.CDATA(tagged_tree)
        single_body_el.append(tagged_content_el)

        # ???
        if stripped_content is not None:
                stripped_content_el = etree.Element("StrippedContent", nsmap=self.ns_map)
                stripped_content_el.text = etree.CDATA(stripped_content)
                single_body_el.append(stripped_content_el)

        # ???
        message_el.xpath("ncdcr:MultiBody", namespaces=self.ns_map)[0].append(single_body_el)
        ##message_el.set("Restricted", str(is_restricted).lower())

        return message_el


    def _get_global_id(self, eaxs_file):
        """ ??? """

        global_id = None
        global_id_el = "{" + self.ncdcr_uri + "}GlobalId"

        # ???
        for event, element in etree.iterparse(eaxs_file, tag=global_id_el):
            global_id_el = element
            global_id = global_id_el.text
            element.clear()

        return global_id


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
            self.logger.error(err)
            raise FileExistsError(err)

        # assume values.
        message_open = False
        current_folder = None

        # prepare attributes for <Account> root.
        global_id = self._get_global_id(eaxs_file)
        source_eaxs = os.path.basename(eaxs_file)

        # write relevant data to "tagged" EAXS file.
        with etree.xmlfile(tagged_eaxs_file, encoding=self.charset, close=True) as xfile:

            # write XML header; permanently register namespace prefix and URI.
            xfile.write_declaration()
            etree.register_namespace("ncdcr", self.ncdcr_uri)

            with xfile.element("ncdcr:Account", GlobalId=global_id, SourceEAXS=source_eaxs,
                    nsmap=self.ns_map):

                for event, element in etree.iterparse(eaxs_file, events=("start", "end",),
                        strip_cdata=False, huge_tree=True):

                    # establish when a <Message> element is open.
                    if event == "start" and element.tag == "{" + self.ncdcr_uri + "}Message":
                        message_open = True
                        continue

                    # tag <Message> elements.
                    if message_open:

                        if (event == "end" and
                                element.tag == "{" + self.ncdcr_uri + "}Message"):
                            message_id = self._get_message_id(element)
                            self.logger.info("Working on message: {}".format(message_id))
                            tagged_message = self._update_message(element, current_folder)
                            xfile.write(tagged_message)
                            element.clear()
                            message_open = False

                    # else, set current <Folder/Name> value.
                    elif not message_open:

                        if (event == "start" and
                                element.tag == "{" + self.ncdcr_uri + "}Name"):
                            current_folder = element.text
                        elif (event == "end" and
                                element.tag == "{" + self.ncdcr_uri + "}Folder"):
                            current_folder = None

                        element.clear()

        return

if __name__ == "__main__":
    pass


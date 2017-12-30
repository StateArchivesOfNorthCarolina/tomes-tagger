#!/usr/bin/env python3

"""
This module contains a class for converting an EAXS file to a tagged EAXS document.

Todo:
    * Do you need to support <ExtBodyContent> messages?
        - I think "yes" and you'll need to append attributes/elements accordingly.
        - I think update_message MIGHT be doing this already?
            - Only one way to find out. :P
    * Do we really want to set @restricted to True if "PII*" is in the tags? If so, need to
    work on that. That's somewhat redundant within the context of search, but I guess we need
    to think of the tagged EAXS as document that's independent of search.
    * Do you really need the decode/encode bit in _get_folder_name()?
    * Investigate JG's Slack comment from 12/22/2017:
        "Another note.  All body-content that is tagged as quoted-printable is now meets that
        specification exactly. If you need to decode for chunking and sending python has a
        tool.
        https://docs.python.org/3/library/quopri.html"
        - I think this is working now but I'll leave this TODO item until I'm more sure.
        - I'm also wondering if I need to check for transfer-encoding and MIME type at the
        multibody level if I don't find it in the <Message> element itself.
    * Do you need to test if there are text AND HTML versions of the email first and default
    to the plain text?
    * _legalize_cdata_text() is stripping a lot of whitespace and mashing words together.
        - I think this is fixed.
    * I think you want to use .strip() for tagged and stripped content to avoid large swaths
    of leading/trailing whitespace.
    * Comment all "???" occurences and uncomment all "!!!" occurences you find.
"""

# import modules.
import base64
import logging
import os
import quopri
import unicodedata
from lxml import etree


class EAXSToTagged():
    """ A class for converting an EAXS file to a tagged EAXS document.

    Example:
        >>> html2text = def html2text(html) ... # convert HTML to plain text.
        >>> text2nlp = def text2nlp(text) ... # convert plain text to NLP/NER output.
        >>> e2t = EAXSToTagged(html2text, text2nlp)
        >>> tagged = e2t.write_tagged(eaxs_file, "output.xml") # tagged EAXS to "output.xml".
    """

    def __init__(self, html_converter, nlp_tagger, charset="UTF-8"):
        """ Sets instance attributes.

        Args:
            - html_converter (function): Any function that accepts HTML text (str) as its
            only required argument and returns a plain text version (str).
            - nlp_tagger (function): Any function that accepts plain text (str) as its only
            required argument and returns an NER-tagged XML message (lxml.etree_Element).
            - charset (str): Encoding with which to update EAXS message content. This is also
            the encoding used to write a tagged EAXS file with the @self.write_tagged() 
            method.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.html_converter = html_converter
        self.nlp_tagger = nlp_tagger
        self.charset = charset

        # set namespace attributes.
        self.ncdcr_prefix = "ncdcr"
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {self.ncdcr_prefix : self.ncdcr_uri}


    @staticmethod
    def _legalize_cdata_text(cdtext, charset, error_handler="backslashreplace"):
        """ ??? """

        # ???
        cdtext = cdtext.replace("\v", "\n").replace("\f", "\n")
        cdtext = "".join([char for char in cdtext if unicodedata.category(char)[0] != "C" or
            char in ("\r", "\t")])
        
        return cdtext
    

    def _get_folder_name(self, message_el):
        """ Gets the folder name for a given <Message> element. Subfolders are preceeded by
        their parent folder name and a forward slash, e.g. 'parent/child'. 
        
        Args:
            message_el (lxml.etree._Element): An EAXS <Message> element.

        Returns:
            str: The return value.
        """

        # iterate through ancestors; collect all ancestral <Folder/Name> element values.
        folder_names = []
        for ancestor in message_el.iterancestors():
            if ancestor.tag == "{" + self.ncdcr_uri + "}Folder":
                name_el = ancestor.getchildren()[0]
                folder_names.insert(0, name_el.text)
            elif ancestor.tag == "{" + self.ncdcr_uri + "}Account":
                break
    
        # convert list to path-like string.
        folder_name = "/".join(folder_names)
        folder_name = folder_name.encode(self.charset, errors="ignore").decode(self.charset)
        
        return folder_name


    def _get_global_id(self, eaxs_file):
        """ Gets the <GlobalId> element value for the given @eaxs_file.
        
        Args:
            - eaxs_file (str): The filepath for the EAXS file.
            
        Returns:
            str: The return value.
        """

        # find <GlobalId> element value and break immediately (to avoid memory spikes!).
        global_id_tag = "{" + self.ncdcr_uri + "}GlobalId"
        for event, element in etree.iterparse(eaxs_file, events=("end",), strip_cdata=False,
                tag=global_id_tag, huge_tree=True):
            global_id_el = element
            global_id = global_id_el.text
            element.clear()
            break

        return global_id


    def _get_messages(self, eaxs_file):
        """ Gets all <Message> elements for the given @eaxs_file.
        
        Args:
            - eaxs_file (str): The filepath for the EAXS file.

        Returns:
            lxml.etree.iterparse: The return value.
        """

        # get generator for all <Message> elements.
        message_tag = "{" + self.ncdcr_uri + "}Message"
        messages = etree.iterparse(eaxs_file, events=("end",), strip_cdata=False, 
                tag=message_tag, huge_tree=True)

        return messages


    def _get_message_id(self, message_el):
        """ Gets the <MessageId> element value for a given <Message> element.

        Args:
            message_el (lxml.etree._Element): An EAXS <Message> element.

        Returns:
            str: The return value.
        """

        # get <MessageId> element value; strip leading/trailing space.
        path = "{}:MessageId".format(self.ncdcr_prefix)
        message_id = message_el.xpath(path, namespaces=self.ns_map)
        message_id = message_id[0].text.strip()

        return message_id


    def _get_single_body_element(self, message_el, name, fallback=""):
        """ Gets the <MultiBody/SingleBody/@name> element and its text value for the given
        parent <Message> element. Note that <SingleBody> elements for attachments are skipped.

        Args:
            - message_el (lxml.etree._Element): An EAXS <Message> element.
            - name (str): The element to retrieve. DO NOT include the @self.ncdcr_prefix 
            namespace prefix (e.g. "ncdcr") as it will be added automatically.
            - fallback (str): The text value to return for @name if no text value is found.

        Returns:
            tuple: The return value.
            The first item is an lxml.etree._Element, i.e. @name.
            The second item is a string, i.e. @name's value.
        """

        # set XPath for @name element, omitting attachments.
        path = "{}:MultiBody".format(self.ncdcr_prefix)
        path += "/SingleBody[(not(contains({}:Disposition, 'attachment')))][1]".format(
                self.ncdcr_prefix)
        path += "/{}".format(name)
        path = path.replace("/", "/{}:".format(self.ncdcr_prefix))

        # get element from @path.
        name_el = message_el.xpath(path, namespaces=self.ns_map)

        # get element values.
        el, el_text = None, fallback
        if len(name_el) > 0:
            name_el = name_el[0]
            el, el_text = name_el, name_el.text

        return (el, el_text)


    def tag_message(self, message_el, content_text):
        """ Tags a given <Message> element with a given text value (@content_text).

        Args:
            - message_el (lxml.etree._Element): An EAXS <Message> element.
            - content_text (str): The text from which to extract NER tags via 
            @self.nlp_tagger.

        Returns:
            tuple: The return value.
            The first item is an lxml.etree._Element: the tagged XML tree.
            The second item is a string: the original message stripped of HTML tags and/or
            Base64-decoded. If the messages was unaltered, this value is None.
        """

        self.logger.info("Tagging <Message> element content.")

        # get <Message> element's transfer encoding and MIME type.
        transfer_encoding_el, transfer_encoding_text = self._get_single_body_element(
                message_el, "TransferEncoding")
        content_type_el, content_type_text = self._get_single_body_element(message_el,
                "ContentType")

        # assume that @content_text will not be altered.
        is_stripped = False

        # if needed, Base64 decode @content_text.
        if transfer_encoding_text.lower() == "base64":
            self.logger.info("Decoding Base64 message content.")
            content_text = base64.b64decode(content_text)
            content_text = content_text.decode(self.charset, errors="backslashreplace")
            is_stripped = True

        # if needed, decode quoted-printable text.
        if transfer_encoding_text.lower() == "quoted-printable":
            self.logger.info("Decoding quoted-printable message content.")
            content_text = quopri.decodestring(content_text)
            content_text = content_text.decode(self.charset, errors="backslashreplace")
            is_stripped = True
        
        # if needed, convert HTML in @content_text to plain text.
        if content_type_text.lower() in ["text/html", "application/xml+html"]:
            self.logger.info("Converting HTML message content to plain text.")
            content_text = self.html_converter(content_text)
            is_stripped = True

        # get NER tags.
        self.logger.info("Tagging message content with NER.")
        tagged_el = self.nlp_tagger(content_text)

        # set value of stripped content.
        stripped_content = None
        if is_stripped:
            stripped_content = content_text

        return (tagged_el, stripped_content)


    def update_message(self, message_el, folder_name):
        """ Updates a <Message> element's value with NER-tagged content. Affixes the 
        @folder_name as a new attribute.

        Args:
            - message_el (lxml.etree._Element): An EAXS <Message> element.
            - folder_name (str): The name of the EAXS <Folder> element that contains the 
            <Message> element.

        Returns:
            lxml.etree._Element: The return value.
            The updated <Message> element.
        """
        
        self.logger.info("Updating <Message> element tree.")

        # set new attributes and elements.
        message_el.set("ParentFolder", folder_name)
        message_el.set("Processed", "false")
        message_el.set("Record", "true")
        message_el.set("Restricted", "true")
        message_el.append(etree.Element("{" + self.ncdcr_uri + "}Restriction", 
            nsmap=self.ns_map))

        # get <Content> element value.
        content_el, content_text = self._get_single_body_element(message_el, 
                "BodyContent/Content")

        # if no <Content> sub-element exists, return the <Message> element.
        if content_el is None or content_text is None:
                return message_el

        # otherwise, get NER tags and a plain text version of the message body.
        tagged_content, stripped_content = self.tag_message(message_el, content_text)

        # create a new <SingleBody> element.
        single_body_el = etree.Element("{" + self.ncdcr_uri + "}SingleBody", 
                nsmap=self.ns_map)

        # create a new <TaggedContent> element; append it to the new <SingleBody> element.
        tagged_content_el = etree.Element("{" + self.ncdcr_uri + "}TaggedContent", 
                nsmap=self.ns_map)
        tagged_content = etree.tostring(tagged_content, encoding=self.charset)
        try:
            tagged_content_el.text = etree.CDATA(tagged_content)
        except ValueError as err:
            self.logger.error(err)
            self.logger.warning("Cleaning tagged content in order to write CDATA.")
            tagged_content = self._legalize_cdata_text(tagged_content, self.charset)
            tagged_content_el.text = etree.CDATA(tagged_content)
        single_body_el.append(tagged_content_el)

        # if needed, append a plain text message body to the new <SingleBody> element.
        if stripped_content is not None:
                stripped_content_el = etree.Element("{" + self.ncdcr_uri + 
                        "}StrippedContent", nsmap=self.ns_map)
                try:
                    stripped_content_el.text = etree.CDATA(stripped_content)
                except ValueError as err:
                    self.logger.error(err)
                    self.logger.warning("Cleaning stripped content in order to write CDATA.")
                    stripped_content = self._legalize_cdata_text(stripped_content, 
                            self.charset)
                    stripped_content_el.text = etree.CDATA(stripped_content)
                single_body_el.append(stripped_content_el)

        # append the new <SingleBody> element to @message_el.
        multi_body_tag = "{}:MultiBody".format(self.ncdcr_prefix)
        message_el.xpath(multi_body_tag, namespaces=self.ns_map)[0].append(single_body_el)

        return message_el


    def write_tagged(self, eaxs_file, tagged_eaxs_file):
        """ Converts an @eaxs_file to a @tagged_eaxs_file.

        Args:
            - eaxs_file (str): The filepath for the EAXS file.
            - tagged_eaxs_file (str): The filepath that the tagged EAXS document will be
            written to.

        Returns:
            None

        Raises:
            - FileExistsError: If @tagged_eaxs_file already exists.
        """

        self.logger.info("Converting '{}' EAXS file to tagged EAXS file: {}".format(
            eaxs_file, tagged_eaxs_file))

        # raise error if output file already exists.
        if os.path.isfile(tagged_eaxs_file):
            err = "Destination file '{}' already exists.".format(tagged_eaxs_file)
            self.logger.error(err)
            #raise FileExistsError(err) # !!! UNDO COMMENT.

        # get count of <Message> elements; prepare data for progress updates.
        total_messages = 0
        self.logger.info("Finding number of messages in source EAXS file.")
        for event, element in self._get_messages(eaxs_file):
            total_messages += 1
            element.clear()
        self.logger.info("Found {} messages.".format(total_messages))
        remaining_messages = total_messages

        # open new @tagged_eaxs_file.
        with etree.xmlfile(tagged_eaxs_file, encoding=self.charset, close=True) as xfile:

            # write XML header to @xfile; register namespace information.
            xfile.write_declaration()
            etree.register_namespace(self.ncdcr_prefix, self.ncdcr_uri)

            # write root <Account> element; append tagged <Message> elements.
            account_tag = "{}:Account".format(self.ncdcr_prefix)
            with xfile.element(account_tag, GlobalId=self._get_global_id(eaxs_file), 
                    SourceEAXS=os.path.basename(eaxs_file), nsmap=self.ns_map):
                
                # tag each <Message> element from source @eaxs_file.
                for event, element in self._get_messages(eaxs_file):
                    
                    # get needed values.
                    message_id = self._get_message_id(element)
                    
                    # DELETE block.
                    if message_id!="<20041004154915.QTXN17040.lakecmmtar01.coxmail.com@Ron>":
                        continue#DELETE !!!
                    
                    folder_name = self._get_folder_name(element)
                    
                    # tag the message and write it to @xfile.
                    self.logger.info("Processing message with id: {}".format(message_id))
                    tagged_message = self.update_message(element, folder_name)
                    xfile.write(tagged_message)
                    element.clear()
                    
                    # report on progress.
                    remaining_messages -= 1
                    self.logger.info("Processing complete for {} of {} messages.".format(
                        (total_messages - remaining_messages), total_messages))
                    if remaining_messages > 0:
                        self.logger.info("Messages left to process: {}".format(
                            remaining_messages))
        
        # report on completion.
        self.logger.info("Finished writing tagged EAXS file: {}".format(tagged_eaxs_file))
        return
  

if __name__ == "__main__":
    pass


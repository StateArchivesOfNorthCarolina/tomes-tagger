#!/usr/bin/env python3

"""
This module contains a class for converting an EAXS file to a tagged EAXS document.

Todo:
    * Do you need to support <ExtBodyContent> messages?
        - I think "yes" and you'll need to append attributes/elements accordingly.
        - I think _update_message() MIGHT be doing this already?
            - Only one way to find out. :P
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
        >>> e2t.write_tagged(eaxs_file, "tagged.xml") # create "tagged.xml".
        >>> e2t.write_tagged(eaxs_file, "tagged.xml", split=True) # create one tagged XML file
        >>> # per message with the form "tagged_01.xml", etc.
        >>> e2t.write_tagged(eaxs_file, "tagged.xml", restrictions=[1,2]) # only output tagged
        >>> # versions of the first two messages.
        >>> e2t.write_tagged(eaxs_file, "tagged.xml", split=True, restrictions=[1,2], 
        >>> inclusive=False) # output tagged versions of all but the first two messages.
    """


    def __init__(self, html_converter, nlp_tagger, charset="UTF-8", buffered=False):
        """ Sets instance attributes.

        Args:
            - html_converter (function): Any function that accepts HTML text (str) as its
            only required argument and returns a plain text version (str).
            - nlp_tagger (function): Any function that accepts plain text (str) as its only
            required argument and returns an NER-tagged XML message (lxml.etree_Element).
            - charset (str): Encoding with which to update EAXS message content. This is also
            the encoding used to write a tagged EAXS file with the @self.write_tagged() 
            method.
            - buffered (bool): Use True to write tagged EAXS files with buffering. Otherwise,
            use False. For more information, see: 
            http://lxml.de/api/lxml.etree.xmlfile-class.html.
        """

        # set logger; suppress logging by default.
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.html_converter = html_converter
        self.nlp_tagger = nlp_tagger
        self.charset = charset
        self.buffered = buffered

        # set namespace attributes.
        self.ncdcr_prefix = "ncdcr"
        self.ncdcr_uri = "http://www.archives.ncdcr.gov/mail-account"
        self.ns_map  = {self.ncdcr_prefix : self.ncdcr_uri}


    @staticmethod
    def _legalize_xml_text(xtext):
        """ A static method that alters @xtext by replacing vertical tabs and form feeds with
        line breaks and removing control characters except for carriage returns and tabs. This
        is so that @xtext can be written to XML without raising a ValueError.
            
        Args:
            - xtext (str): The text to alter.

        Returns:
            str: The return value.
        """

        # legalize @xtext.
        for ws in ["\f","\r","\v"]:
            xtext = xtext.replace(ws, "\n")
        xtext = "".join([char for char in xtext if unicodedata.category(char)[0] != "C" or
            char in ("\t", "\n")])
        
        return xtext


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
                if name_el.tag == "{" + self.ncdcr_uri + "}Name" and name_el.text != None:
                    folder_names.insert(0, name_el.text)
            elif ancestor.tag == "{" + self.ncdcr_uri + "}Account":
                break
    
        # convert list to path-like string.
        folder_name = "/".join(folder_names)
        folder_name = folder_name.encode(self.charset).decode(self.charset, errors="ignore")
        
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
        path = "{ns}:MessageId".format(ns=self.ncdcr_prefix)
        message_id = message_el.xpath(path, namespaces=self.ns_map)
        message_id = message_id[0].text.strip()

        return message_id

    
    def _get_message_data(self, message_el):
        """ Gets relevant element values from the given <Message> element, @message_el.
        
        Args:
            - message_el (lxml.etree._Element): An EAXS <Message> element.
        
        Returns:
            tuple: The return value.
            All items are strings.
            The first item is the message's <BodyContent/Content> element value.
            The second item is the <BodyContent/TransferEncoding> element value.
            The third item is the <ContentType> element value.
        """

        # set XPath for <SingleBody> elements, omitting attachments.
        path = "{ns}:MultiBody/{ns}:SingleBody[not(descendant::{ns}:Disposition)]"
        path = path.format(ns=self.ncdcr_prefix)
        
        # assume default values.
        content_text, transfer_encoding_text, content_type_text = "", "7-bit", "text/plain"

        # get all <SingleBody> elements via XPath.
        single_body_els = message_el.xpath(path, namespaces=self.ns_map)
        for single_body_el in single_body_els:
            
            # set @content_text.
            node = "{ns}:BodyContent/{ns}:Content".format(ns=self.ncdcr_prefix)
            content_el = single_body_el.xpath(node, namespaces=self.ns_map)
            if len(content_el) > 0 and content_el[0].text is not None:
                content_text = content_el[0].text
            else:
                content_text = ""

            # set @transfer_encoding_text.
            node = "{ns}:BodyContent/{ns}:TransferEncoding".format(ns=self.ncdcr_prefix)
            transfer_el = single_body_el.xpath(node, namespaces=self.ns_map)
            if len(transfer_el) > 0 and transfer_el[0].text is not None:
                transfer_encoding_text = transfer_el[0].text.lower()
            else:
                transfer_encoding_text = ""

            # set @content_type_text.
            node = "{ns}:ContentType".format(ns=self.ncdcr_prefix)
            content_type_el = single_body_el.xpath(node, namespaces=self.ns_map)
            if len(content_type_el) > 0 and content_type_el[0].text is not None:
                content_type_text = content_type_el[0].text.lower()
            else:
                content_type_text = ""
 
            # if the preferred plain/text message is found, break immediately.
            if content_type_text == "text/plain":
                break

        # return data as tuple.
        message_data = (content_text, transfer_encoding_text, content_type_text)
        return message_data


    def _tag_message(self, content_text, transfer_encoding_text, content_type_text):
        """ Tags a given <Message> element with a given text value (@content_text) and given
        @transfer_encoding_text and @content_type_text values.

        Args:
            - content_text (str): The text from which to extract NER tags via 
            @self.nlp_tagger.
            - transfer_encoding_text (str): The message's transfer encoding value.
            - content_type_text (str): The message's content type value.

        Returns:
            tuple: The return value.
            The first item is an lxml.etree._Element: the tagged XML tree.
            The second item is a string: the original message stripped of HTML tags and/or
            Base64-decoded and/or decoded quoted-printable. If the messages was unaltered,
            this value is None.
        """

        self.logger.info("Tagging <Message> element content.")

        # assume that @content_text will not be altered.
        is_stripped = False

        # if needed, Base64 decode @content_text.
        if transfer_encoding_text == "base64":
            self.logger.info("Decoding Base64 message content.")
            content_text = base64.b64decode(content_text)
            content_text = content_text.decode(self.charset, errors="backslashreplace")
            is_stripped = True

        # if needed, decode quoted-printable text.
        if transfer_encoding_text == "quoted-printable":
            self.logger.info("Decoding quoted-printable message content.")
            content_text = quopri.decodestring(content_text)
            content_text = content_text.decode(self.charset, errors="backslashreplace")
            is_stripped = True
        
        # if needed, convert HTML in @content_text to plain text.
        if content_type_text in ["text/html", "application/xml+html"]:
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


    def _update_message(self, message_el, folder_name):
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
        try:
            message_el.set("ParentFolder", folder_name)
        except ValueError as err:
            self.logger.error(err)
            self.logger.info("Cleaning @ParentFolder attribute value.")
            message_el.set("ParentFolder", self._legalize_xml_text(folder_name))
        message_el.set("Processed", "false")
        message_el.set("Record", "true")
        message_el.set("Restricted", "false")
        message_el.append(etree.Element("{" + self.ncdcr_uri + "}Restriction", 
            nsmap=self.ns_map))

        # get relevant <Message> element data.
        message_data = self._get_message_data(message_el)
        content_text, transfer_encoding_text, content_type_text = message_data

        # if no viable <Content> sub-element exists, return the <Message> element.
        if content_text == "":
            self.logger.warning("Found empty message content; skipping message tagging.")
            return message_el

        # otherwise, get NER tags and a plain text version of the message body.
        tagged_content, stripped_content = self._tag_message(content_text, 
                transfer_encoding_text, content_type_text)

        # if PII appears to exist in the message; update the @Restricted attribute.
        token_el = "{" + self.ncdcr_uri + "}Token"
        for element in tagged_content.iterchildren(tag=token_el):
            if "entity" not in element.attrib:
                continue
            if element.attrib["entity"][:4] == "PII.":
                self.logger.info("Found PII tag; updating messages's @Restricted attribute.")
                message_el.set("Restricted", "true")
                break

        # create a new <SingleBody> element.
        single_body_el = etree.Element("{" + self.ncdcr_uri + "}SingleBody", 
                nsmap=self.ns_map)

        # create a new <TaggedContent> element; append it to the new <SingleBody> element.
        tagged_content_el = etree.Element("{" + self.ncdcr_uri + "}TaggedContent", 
                nsmap=self.ns_map)
        tagged_content = etree.tostring(tagged_content, encoding=self.charset)
        tagged_content = tagged_content.decode(self.charset, errors="backslashreplace")
        try:
            tagged_content_el.text = etree.CDATA(tagged_content.strip())
        except ValueError as err:
            self.logger.error(err)
            self.logger.warning("Cleaning tagged content in order to write CDATA.")
            tagged_content = self._legalize_xml_text(tagged_content)
            tagged_content_el.text = etree.CDATA(tagged_content.strip())
        single_body_el.append(tagged_content_el)

        # if needed, append a plain text message body to the new <SingleBody> element.
        if stripped_content is not None:
                stripped_content_el = etree.Element("{" + self.ncdcr_uri + 
                        "}StrippedContent", nsmap=self.ns_map)
                try:
                    stripped_content_el.text = etree.CDATA(stripped_content.strip())
                except ValueError as err:
                    self.logger.error(err)
                    self.logger.info("Cleaning stripped content in order to write CDATA.")
                    stripped_content = self._legalize_xml_text(stripped_content)
                    stripped_content_el.text = etree.CDATA(stripped_content.strip())
                single_body_el.append(stripped_content_el)

        # append the new <SingleBody> element to @message_el.
        multi_body_tag = "{ns}:MultiBody".format(ns=self.ncdcr_prefix)
        message_el.xpath(multi_body_tag, namespaces=self.ns_map)[0].append(single_body_el)

        return message_el

    
    def _get_tagged_messages(self, eaxs_file, total_messages, restrictions=[], 
            inclusive=True):
        """ Tags <Message> elements in a given @eaxs_file.
        
        Args:
            - eaxs_file (str): The filepath for the EAXS file.
            - total_messages (int): The total number of <Message> elements in @eaxs_file.
            - restrictions (list): The position of the messages to exclusively tag OR those
            to skip from tagging. Note: the first message's value is 1. Leave this empty to
            tag all messages.
            - inclusive (bool): Use True to only tag messages whose position values are in
            @restrictions. Otherwise, use False to tag all messages except the ones listed in
            @restrictions. If @restrictions is empty, this value is ignored.
            
        Returns:
            generator: The return value.
            The yielded data is a tuple.
            The first item is a string, the zero-padded position of the given message (first =
            1). The second item is the <MessageId> value. The third item is the tagged 
            lxml.etree._Element or None if the tagging workflow failed.
        """
        
        self.logger.info("Tagging messages in EAXS file: {}".format(eaxs_file))

        # tag each <Message> element.
        message_index = 0
        for event, element in self._get_messages(eaxs_file):

            message_index += 1
            
            # if @restrictions is not empty; filter results as requested.            
            if len(restrictions) != 0:
                msg = "Skipping message {} as requested.".format(message_index)
                if inclusive and message_index not in restrictions:
                    self.logger.info(msg)
                    continue
                elif not inclusive and message_index in restrictions:
                    self.logger.info(msg)
                    continue
            
            # get needed values from the message element.
            message_id = self._get_message_id(element)
            folder_name = self._get_folder_name(element)

            # tag the message.
            self.logger.info("Tagging message with id: {}".format(message_id))
            try:
                tagged_message = self._update_message(element, folder_name)
            except Exception as err:
                self.logger.error(err)
                self.logger.warning("Failed to complete tagging workflow.")
                tagged_message = None

            # report on progress.
            remaining_messages = total_messages - message_index
            self.logger.info("Processed {} of {} messages.".format(message_index, 
                total_messages))
            if remaining_messages > 0:
                self.logger.info("Messages left to process: {}".format(remaining_messages))
            
            # yield the tagged message tuple.
            yield (message_index, message_id, tagged_message)
            
            # clear original @element (must follow yield!).
            element.clear()

        return


    def _write_xml(self, eaxs_file, tagged_eaxs_file, tagged_messages, global_id):
        """ Writes @tagged_eaxs_file as an XML file.

        Args:
            - eaxs_file (str): The filepath for the EAXS file.
            - tagged_eaxs_file (str): The filepath to which the tagged EAXS document will be
            written.
            - tagged_messages (generator): The tagged message tuple as returned by 
            self._get_tagged_messages().
            - global_id (str): The value of self._get_global_id(@eaxs_file).

        Returns:
            list: The return value.
            The message indexes for messages that failed to finish the tagging process.

        Raises:
            - FileExistsError: If @tagged_eaxs_file already exists.
        """

        # raise error if @tagged_eaxs_file already exists.
        if os.path.isfile(tagged_eaxs_file):
            err = "Destination file '{}' already exists.".format(tagged_eaxs_file)
            self.logger.error(err)
            raise FileExistsError(err)

        # create placeholder for untagged messages.
        untagged_messages = []
        
        # open new @tagged_eaxs_file.
        with etree.xmlfile(tagged_eaxs_file, encoding=self.charset, close=True, 
                buffered=self.buffered) as xfile:

            # write XML header to @xfile; register namespace information.
            xfile.write_declaration()
            etree.register_namespace(self.ncdcr_prefix, self.ncdcr_uri)

            # write root <Account> element; append tagged <Message> elements.
            account_tag = "{ns}:Account".format(ns=self.ncdcr_prefix)
            with xfile.element(account_tag, GlobalId=global_id, SourceEAXS=eaxs_file, 
            nsmap=self.ns_map):
                
                # write tagged message to file.
                for message_index, message_id, tagged_message in tagged_messages:
                    
                    # if message wasn't tagged, append index to @untagged_messages.
                    if tagged_message is None:
                        untagged_messages.append(message_index)
                    
                    # otherwise, write message.
                    else:
                        xfile.write(tagged_message)
                        tagged_message.clear()
            
            return untagged_messages


    def write_tagged(self, eaxs_file, tagged_eaxs_file, split=False, restrictions=[], 
            inclusive=True):
        """ Converts an @eaxs_file to one or many tagged EAXS file/s.
            
        Args:
            - eaxs_file (str): The filepath for the EAXS file.
            - tagged_eaxs_file (str): The filepath that the tagged EAXS document will be
            written to. If @split is True, this value will have an underscore and the
            zero-padded position of each message placed before the file extension.
            - split (bool): Use True to create one tagged EAXS file per message. Otherwise,
            use False.
            - restrictions (list): The position of the messages to exclusively tag OR those
            to skip from tagging. Note: the first message's value is 1. Leave this empty to
            tag all messages.
            - inclusive (bool): Use True to only tag messages whose position values are in
            @restrictions. Otherwise, use False to tag all messages except the ones listed in
            @restrictions. If @restrictions is empty, this value is ignored.
        
        Returns:
            dict: The return type.
            The "message_count" key's value is and int, the total number of messages in 
            @eaxs_file. The "untagged_messages" key's value is a list of ints - the message
            indexes of <Message> elements that didn't make it through the tagging workflow.

        Raises:
            - FileNotFoundError: If @eaxs_file doesn't exist or if the containing folder for 
            @tagged_eaxs_file doesn't exist.
        """

        # raise error if @eaxs_file doesn't exist.
        if not os.path.isfile(eaxs_file):
            err = "Can't find EAXS file: {}".format(eaxs_file)
            self.logger.error(err)
            raise FileNotFoundError(err)

        # raise error if containing folder for @tagged_eaxs_file does not exist.
        container = os.path.split(tagged_eaxs_file)[0]
        if container != "" and not os.path.isdir(container):
            err = "Destination folder '{}' does not exist.".format(container)
            self.logger.error(err)
            raise FileNotFoundError(err)
        
        # get count of <Message> elements.
        msg = "Finding number of messages in '{}'; this may take a while.".format(eaxs_file)
        self.logger.info(msg) 
        total_messages = 0
        for event, element in self._get_messages(eaxs_file):
            total_messages += 1
            element.clear()
        self.logger.info("Found {} messages.".format(total_messages))
        
        # get needed values for @eaxs_file.
        global_id = self._get_global_id(eaxs_file)
        source_eaxs = os.path.basename(eaxs_file)
        
        # launch generator to tag all messages.
        tagged_messages = self._get_tagged_messages(eaxs_file, total_messages, restrictions,
                inclusive)

        # create placeholder dict to return.
        results = {"total_messages": total_messages, "untagged_messages": []}

        # create function to write one file per message.
        def multi_file_writer():

            # determine padding length based on @total_messages.
            padding_length = 1 + len(str(total_messages))
            
            # lambda functions to return a padded version of @tagged_eaxs_file.
            pad_indx = lambda indx: "_" + str(indx).zfill(padding_length) 
            pad_file = lambda fname, pad: pad.join(os.path.splitext(fname))
            
            # write one file per each message.
            for tagged_message in tagged_messages:
                msg_indx = tagged_message[0]
                fname = pad_file(tagged_eaxs_file, pad_indx(msg_indx))
                untagged = self._write_xml(source_eaxs, fname, [tagged_message], global_id)
                results["untagged_messages"] += untagged
            
            return results

        # create function to write only one file.
        def single_file_writer():
            
            untagged = self._write_xml(source_eaxs, tagged_eaxs_file, tagged_messages, 
                    global_id)
            results["untagged_messages"] = untagged
            
            return results

        # execute the appropriate function depending on the value of @split.
        if split:
            results = multi_file_writer()
        else:
            results = single_file_writer()

        return results


if __name__ == "__main__":
    pass


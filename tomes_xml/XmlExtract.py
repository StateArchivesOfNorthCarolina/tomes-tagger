# -*- coding: utf-8 -*-
import logging
import re
import xml.etree.cElementTree as ET
from Message import MessageBlock as MesBlock


class XmlElementSearch:
    """A class to extract elements from XML giving an element name and a namespace
    """
    requested_element = []

    def __init__(self, element, namespace, logger=None):
        self.logger = logger or logging.getLogger()
        self.con_log = logging.getLogger('console_info')

        self.search_element = element
        self.ns = "{"+namespace+"}"
        self.tag = self.ns + self.search_element
        self.msg = None
        self.clean = None
        self.msgs = []
        self.count = 0

    def get_contents(self, fi):
        self.logger.info("Parsing the EAXS file...")
        context = ET.iterparse(fi, events=('start', 'end'))
        context = iter(context)
        event, root = context.next()
        for event, elem in context:
            if event == 'end' and elem.tag == self.tag:
                self.count += 1
                self.con_log.info("Extracting message {}".format(self.count))
                msg = MesBlock(elem, self.ns)
                self.msgs.append(msg)
                root.clear()


class XmlCleanElements:
    """A class to define methods for cleaning up an elements contents
    """

    def __init__(self, el, clean_pattern, logger=None):
        """
        @type el list[Message.MessageBlock]
        @rtype list[Message.MessageBlock]
        """
        self.logger = logger or logging.getLogger()
        self.console_log = logging.getLogger('console_info')
        self.el = el
        self.cleaned_list = []

        if isinstance(clean_pattern, list):
            self.multiple_clean(clean_pattern)
        else:
            self.single_clean(clean_pattern)

    def single_clean(self, pattern):
        count = 0
        for elem in self.el:
            """
            @type elem Message.MessageBlock
            """
            self.console_log.info('Filtering message {}'.format(elem.message_id))
            try:
                if not re.match(pattern, elem.content[0]):
                    self.cleaned_list.append(elem)
                    continue
                count += 1
            except IndexError:
                self.logger.error("This message had no content {}".format(elem.message_id))
                count += 1
            except AttributeError:
                self.logger.error("This message had no content {}".format(elem.message_id))
                count += 1
        self.logger.info("{} messages removed based on regexes".format(count))

    def multiple_clean(self, patterns):
        count = 0
        for elem in self.el:
            """
            @type elem Message.MessageBlock
            """
            no_match = True
            self.console_log.info('Filtering message {}'.format(elem.message_id))
            for pat in patterns:
                try:
                    if re.match(pat, elem.content[0]):
                        no_match = False
                except IndexError as e:
                    self.logger.error("This message had no content {}".format(elem.message_id))
                    count += 1
                except AttributeError as e:
                    self.logger.error("This message had no content {}".format(elem.message_id))
                    count += 1

            if no_match:
                # The pattern did not match on the message add message to the list
                self.cleaned_list.append(elem)
            else:
                # The pattern did match
                count += 1
        self.logger.info("{} messages removed based on regexes or because no content".format(count))


class XmlDedupeElements:
    """ A class to remove duplicate Messages

    """

    def __init__(self, el, logger=None):
        """
        @type el list[Message.MessageBlock]
        @rtype list[Message.MessageBlock]
        """
        self.logger = logger or logging.getLogger()
        self.console_log = logging.getLogger('console_info')
        self.el = el
        self.deduped_list = []
        self.list_of_ids = []

        for elem in self.el:
            """
            @type elem Message.MessageBlock
            """
            if elem.message_id in self.list_of_ids:
                continue
            else:
                self.list_of_ids.append(elem.message_id)
                self.deduped_list.append(elem)

        self.logger.info("Found {} duplicate messages, and removed them from the corpus."
                         .format((len(self.el) - len(self.deduped_list))))
        print()

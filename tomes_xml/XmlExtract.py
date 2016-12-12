#!/usr/bin/python

"""
TO DO:
    - add file docstring.
    - for XmlDedupeElements, maybe check if each list member isinstance() Message.MessageBlock; log error if not.
        - that will help document what needs to be passed to it.
    - worker logic in XmlDedupeElements.__init__ should ideally be moved to a separate method.
    - see if you can get rid of the print() statement in XmlDedupeElements.
        - Try to add new line to logging format per http://stackoverflow.com/a/8735999.
    - @clean_pattern in XmlCleanElements should always be a list (even if there's only one item).
        - this would eliminate need to have two cleaning functions since the cleaning function will always iterate over a list.
        - that way __init__ doesn't need to call one of the cleaners since there will only be one cleaner.
        - actually: use a tuple instead since it's not mutable.
"""

# import modules.
import logging
import re
import xml.etree.cElementTree as ET
from Message import MessageBlock

class XmlElementSearch(object):
    """Extracts elements from an XML file."""
    
    requested_element = [] # ??? DELETE? Not used.

    def __init__(self, element, namespace, logger=None):
        """Sets initial attributes to parse a given XML @element with a given @namespace.
        
        Keyword arguments:
        
        @type element string
        @type namespace string
        @type logger logging.RootLogger???
        """
        
        # sets logging.
        self.logger = logger or logging.getLogger()
        self.con_log = logging.getLogger("console_info")

        # set attributes.
        self.search_element = element
        self.ns = "{"+namespace+"}"
        self.tag = self.ns + self.search_element
        self.msg = None # ??? DELETE? Not used.
        self.clean = None # ??? DELETE? Not used.
        self.msgs = []
        self.count = 0

    def get_contents(self, eaxs_file):
        """Appends MessageBlock instances to self.msgs from content in file @eaxs_file.
        
        Keyword arguments:
        
        @type eaxs_file string
        """
        
        # parse EAXS file.
        self.logger.info("Parsing the EAXS file...")
        context = ET.iterparse(eaxs_file, events=("start", "end"))
        context = iter(context)
        event, root = context.next()
        
        # if occurrence of self.tag if found and closed:
        # increments self.count and appends MessageBlock instances to self.msgs.
        for event, elem in context:
            if event == "end" and elem.tag == self.tag:
                self.count += 1
                self.con_log.info("Extracting message %d", self.count)
                msg = MessageBlock(elem, self.ns)
                self.msgs.append(msg)
                root.clear()

class XmlCleanElements(object):
    """Cleanses an XML element's contents."""

    def __init__(self, el, clean_pattern, logger=None):
        """Cleans MessageBlock items in list @el with a given regex @clean_pattern.
        Note: @clean_pattern can be a regex pattern string or a list of them.
        
        Keyword arguments:
        
        @type el list
        @type clean_pattern string OR list
        @type logger logging.RootLogger???
        """
        
        # sets logging.
        self.logger = logger or logging.getLogger()
        self.console_log = logging.getLogger("console_info")
        
        # sets attributes.
        self.el = el # list of MessageBlock items.
        self.cleaned_list = [] # store MessageBlocks without a pattern match.

        # calls appropriate cleaner depending on type of @clean_pattern.
        if isinstance(clean_pattern, list):
            self.multiple_clean(clean_pattern)
        else:
            self.single_clean(clean_pattern)

    def single_clean(self, pattern):
        """Adds MessageBlock item to self.cleaned_list if regex @pattern does not match against MessageBlock.content.
        
        Keyword arguments:
        
        @type pattern string
        """
        
        # iterate through MessageBlock items; test for match.
        count = 0
        for elem in self.el:
            self.console_log.info("Filtering message %s", elem.message_id)
            try:
                if not re.match(pattern, elem.content[0]): # if no pattern match, then add MessageBlock to clean list.
                    self.cleaned_list.append(elem)
                    continue
                count += 1 # increment @count only if pattern matched.
            except (IndexError, AttributeError):
                self.logger.error("This message had no content %s", elem.message_id)
                count += 1
        self.logger.info("%d messages removed based on regexes", count)

    def multiple_clean(self, patterns):
        """Adds MessageBlock item to self.cleaned_list if no regex pattern in @patterns matches against MessageBlock.content.
        
        Keyword arguments:
        
        @type patterns list
        """
        
        # iterate through MessageBlock items; test for matches.
        count = 0
        for elem in self.el:
            no_match = True
            self.console_log.info("Filtering message %s", elem.message_id)
            
            # iterate through each regex pattern; change @no_match to False if pattern found.
            for pat in patterns:
                try:
                    if re.match(pat, elem.content[0]):
                        no_match = False
                        # ??? can we break out of the for loop at this point? i.e. since we only need to find one match before excluding the message.
                except (IndexError, AttributeError):
                    self.logger.error("This message had no content %s", elem.message_id)
                    count += 1

            # if no patterns matched, then add MessageBlock to clean list.
            # otherwise, increment @count.
            if no_match:
                self.cleaned_list.append(elem)
            else:
                count += 1
        self.logger.info("%d messages removed based on regexes", count)

class XmlDedupeElements(object):
    """Removes duplicate Message.MessageBlock objects from a given list."""

    def __init__(self, el, logger=None):
        """Removes duplicates from a list @el of Message.MessageBlock objects.
        Logs numbers of duplicate messages that were removed.
        
        Keyword arguments:
        
        @type el list
        @type logger logging.RootLogger???
        """
        
        # set initial instance attributes.
        self.logger = logger or logging.getLogger()
        self.console_log = logging.getLogger("console_info")
        self.el = el
        self.deduped_list = []
        self.list_of_ids = []

        # add message identifier to tracking lists.
        for elem in self.el:
            if elem.message_id in self.list_of_ids:
                continue
            else:
                self.list_of_ids.append(elem.message_id)
                self.deduped_list.append(elem)

        # log message about duplicate findings.
        difference = len(self.el) - len(self.deduped_list)
        self.logger.info("Found %d duplicate messages, and removed them from the corpus.", difference)
        print()

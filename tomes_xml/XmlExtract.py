# -*- coding: utf-8 -*-
import re
import sys
import xml.etree.ElementTree as ET

import PickleMsg
from FromStats import FromStat
from Message import MessageBlock as MesBlock
import logging
import gzip
import shutil

class XmlElementSearch:
    """A class to extract elements from XML giving an element name and a namespace
    """
    requested_element = []

    def __init__(self, f, element, namespace, logger=None):
        self.logger = logger or logging.getLogger()

        self.search_element = element
        self.ns = "{"+namespace+"}"
        self.tag = self.ns + self.search_element
        self.msg = None
        self.clean = None
        self.msgs = []
        self.count = 0

        self.tree = ET.parse(f)
        self.root = self.tree.getroot()
        # self.gzip_xml(f)

    def get_contents_of_element(self):
        nsp = self.ns + self.search_element
        elements = list(self.root.iter(nsp))
        self.count = len(elements)
        for elem in elements:
            self.logger.info("Processing: " + str(self.count))
            self.count -= 1
            self.msg = MesBlock(elem, self.ns)
            self.msgs.append(self.msg)

    def get_contents(self, item):
        context = ET.iterparse(item, events=('start', 'end'))
        _, root = next(context)
        for event, elem in context:
            if event == 'end' and elem.tag == self.tag:
                yield elem
                root.clear()

    def gzip_xml(self, f):
        with open(f, 'rb') as f_in, gzip.open('gziped_xml_account.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    def gunzip_xml(self, f):
        file_content = None
        with gzip.open(f, 'rb') as f:
            file_content = f.read()

        return file_content

class XmlCleanElements:
    """A class to define methods for cleaning up an elements contents
    """

    def __init__(self, el, clean_pattern, logger=None):
        """
        @type el list[Message.MessageBlock]
        @rtype list[Message.MessageBlock]
        """
        self.logger = logger or logging.getLogger()
        self.el = el
        self.cleaned_list = []

        if isinstance(clean_pattern, list):
            self.multiple_clean(clean_pattern)
        else:
            self.single_clean(clean_pattern)

    def single_clean(self, pattern):
        for elem in self.el:
            """
            @type elem Message.MessageBlock
            """
            try:
                if not re.match(pattern, elem.content[0]):
                    self.cleaned_list.append(elem)
            except IndexError as e:
                self.logger.error(e.message)
            except AttributeError as e:
                self.logger.error(e.message)

    def multiple_clean(self, patterns):
        for elem in self.el:
            """
            @type elem Message.MessageBlock
            """
            for pat in patterns:
                try:
                    if not re.match(pat, elem.content[0]):
                        self.cleaned_list.append(elem)
                except IndexError as e:
                    self.logger.error(e.message)
                except AttributeError as e:
                    self.logger.error(e.message)


def first_build():
    print("Searching Elements...\n")
    xes = XmlElementSearch(sys.argv[1], sys.argv[2], sys.argv[3])
    print("Cleaning Elements...\n")
    xce = XmlCleanElements(xes.msgs, '^.*[0-9]+:[0-9]+ [A-Z]+.:')
    print("Cleaning Elements...\n")
    xce = XmlCleanElements(xce.cleaned_list, '[A-Z]+:[A-Z]+\\n')
    print("Cleaning Elements...\n")
    xce = XmlCleanElements(xce.cleaned_list, '^\\n\\n-+.[a-zA-Z]+ [a-zA-Z]+.-+\\n')
    print("Serializing Messages...")

    pickler = PickleMsg.TomesPickleMsg(xce.cleaned_list)
    pickler.serialize()





if __name__ == "__main__":
    # Run if changes needed such as class modifications
    # first_build()

    # msgs = unpickle()

    # clean = ContentCleaner(msgs)
    # clean.set_message_ratios()
    # msgs = clean.msgs
    msgs = unpickle()
    fs = FromStat()
    for m in msgs:
        tup = []
        for a, b in m.sentence_vectors:
            tup.append(b)
        fs.set_message_shape(tuple(tup), m.from_id)

    pickle(fs, "from_stats.pkl")
from tomes_xml.XmlExtract import XmlElementSearch
from tomes_xml.XmlExtract import XmlCleanElements
from tomes_xml.XmlExtract import XmlDedupeElements

from tomes_xml.PickleMsg import TomesPickleMsg
import logging
import logging.config
import yaml
import argparse
from regexs.email_cleaners import skype_conversations


def load_logger():
    f = open('logging.yml', 'rt')
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def create_parser():
    aparser = argparse.ArgumentParser()
    aparser.add_argument('-t', '--toolchain', type=str, nargs=1, help='The part of the toolchain to use.',
                         choices=['extract', 'clean', 'process'])
    aparser.add_argument('-f', '--file', type=str, nargs='?', help='a file path, if required by the toolchain.')
    aparser.add_argument('-a', '--arguments', type=str, nargs='+', help='arguments required by the toolchain')
    return aparser


def extractor(args):
    log.info("Searching on {} {} {}".format(args.file, args.arguments[0], args.arguments[1]))
    xes = XmlElementSearch(args.arguments[0], args.arguments[1])
    log.info("Beginning Search...")
    xes.get_contents(args.file)
    log.info("Search Ended: {} messages found.".format(len(xes.msgs)))
    log.info("Serializing to: {}".format(TomesPickleMsg.default_loc))
    pickler = TomesPickleMsg(xes.msgs)
    pickler.serialize()
    log.info("Finished Extracting Messages from EAXS XML file.")


def cleaner(msg_list=None):
    if msg_list:
        xce = XmlCleanElements(msg_list, skype_conversations)
    else:
        unpickler = TomesPickleMsg()
        log.info("Deserializing Emails...")
        msgs = unpickler.deserialize()
        log.info("Cleaning emails based on regexs...")
        xce = XmlCleanElements(msgs, skype_conversations)
        xde = XmlDedupeElements(xce.cleaned_list)
        unpickler.serialize(xce.cleaned_list, 'cleaned_msgs.pkl')


def test_answer():
    assert True

if __name__ == "__main__":
    load_logger()
    log = logging.getLogger()
    psr = create_parser()
    args = psr.parse_args()
    tc = args.toolchain

    if tc[0] == 'extract':
        extractor(args)
    elif tc[0] == 'clean':
        cleaner()
    elif tc[0] == 'process':
        pass

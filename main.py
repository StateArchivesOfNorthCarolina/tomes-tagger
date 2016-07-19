from tomes_xml.XmlExtract import XmlElementSearch
from tomes_xml.PickleMsg import TomesPickleMsg
import sys
import logging
import logging.config
import yaml


def load_logger():
    f = open('logging.yaml', 'rt')
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

if __name__ == "__main__":
    load_logger()
    log = logging.getLogger()

    xml_file = None
    element_to_find = None
    namespace = None
    if sys.argv:
        xml_file = sys.argv[1]
        element_to_find = sys.argv[2]
        namespace = sys.argv[3]
    else:
        log.info("there are no arguments")
        sys.exit(1)

    log.info("Searching on {} {} {}\n".format(xml_file, element_to_find, namespace))

    xes = XmlElementSearch(xml_file, element_to_find, namespace)
    log.info("Begining Search...")
    xes.get_contents_of_element()
    log.info("Search Ended: {} messages found.".format(len(xes.msgs)))
    pickler = TomesPickleMsg(xes.msgs)
    pickler.serialize()

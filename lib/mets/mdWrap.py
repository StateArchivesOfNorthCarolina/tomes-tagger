#!/usr/bin/env python3

"""
This module creates a METS <mdWrap> tree for given input. The output can be integrated into a
complete METS file's <dmdSec> element.

TODO:
    - ???
"""

# import modules.
import mets_ns
from lxml import etree


def mdWrap(metadata, mdtype, attributes=None):
    """ Creates a METS <mdWrap> etree element.

    Args:
        - metadata (lxml.etree._Element): The metadata to wrap in the <mdWrap> element.
        - mdtype (str): The MDTYPE attribute value to set for the <mdwrap>.
        - attributes (dict): The optional attributes to set for the <mdWrap>.
    
    Returns:
        <class 'lxml.etree._Element'>
    """
    
    # create <mdWrap> element; set optional attributes and MDTYPE attribute.
    mdWrap_el = etree.Element(mets_ns.ns_id + "mdWrap", nsmap=mets_ns.ns_map)
    if attributes is not None:
        for k, v in attributes.items():
            mdWrap_el.set(k, v)
    mdWrap_el.set("MDTYPE", mdtype)

    # create <xmlData> subelement; append @metadata tree.
    xmlData_el = etree.SubElement(mdWrap_el, mets_ns.ns_id + "xmlData", nsmap=mets_ns.ns_map)
    xmlData_el.append(metadata)

    return mdWrap_el


# TEST.
def main():
    
    # create Dublin Core tree.
    from dcxml import simpledc
    md = dict(titles = ["Test"],
            descriptions = ["A test."])
    md = simpledc.dump_etree(md)

    # wrap Dublin Core.
    mdwrap = mdWrap(md, "DC", {"ID":"Test Metadata"})

    # print XML.
    mdwrapx = etree.tostring(mdwrap, pretty_print=True)
    mdwrapx = mdwrapx.decode("utf-8")
    print(mdwrapx)

if __name__ == "__main__":
    main()


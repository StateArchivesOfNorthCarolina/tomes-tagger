#!/usr/bin/env python3

"""
This module creates a METS <div> tree for a given list of files. The output can be integrated
into a complete METS file's <structMap> element.

TODO:
    - ???
"""

# import modules.
import mets_ns
from lxml import etree


def div(file_ids, attributes=None):
    """ Creates a METS <div> etree element for each item in @file_ids.

    Args:
        - file_ids (list): The identifiers to use for each <fptr> element within the <div>.
        - attributes (dict): The optional attributes to set for the <div>.
    
    Returns:
        <class 'lxml.etree._Element'>
    """
    
    # create <div> element for ...; set ID and optional attributes.
    div_el = etree.Element(mets_ns.ns_id + "div", nsmap=mets_ns.ns_map)
    if attributes is not None:
        for k, v in attributes.items():
            div_el.set(k, v)

    for file_id in file_ids:  

        # create <fptr> element for current file; set FILEID attribute.
        fptr_el = etree.SubElement(div_el, mets_ns.ns_id + "fptr", nsmap=mets_ns.ns_map)
        fptr_el.set("FILEID", file_id)

    return div_el


# TEST.
def main():

    # create list of test ids.
    file_ids = [str(i) for i in range(0,10)]
    
    # create <div> with some attributes.
    divider = div(file_ids, {"ID": "test", "LABEL": "testing"})

    # print XML.
    dividerx = etree.tostring(divider, pretty_print=True)
    dividerx = dividerx.decode("utf-8")
    print(dividerx)

if __name__ == "__main__":
    main()


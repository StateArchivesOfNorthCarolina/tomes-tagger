#!/usr/bin/env python3

"""
This module contains a function for creating RDF/Dublin Core metadata from a Microsoft Excel
2010 file (.xlsx).

Todo:
    * Add logging.
    * Need to actually output entire mets:mdWrap. So maybe this shouldn't be an "extension"?
        - Well, pymets will actually do the wrapping IF you pass a dict not a list so that
        the sheet name is available to pymets.
"""

# import modules.
import sys; sys.path.append("..")
import hashlib
import logging
from datetime import datetime
from lxml import etree
from openpyxl import load_workbook
from lib.anyType import *
from lib.namespaces import rdf_dc_ns


def excel_to_rdf(xlsx_path, element_header="dc_element", value_header="dc_value"):
    """ A function for creating RDF/Dublin Core metadata from a Microsoft Excel 2010 file 
    (.xlsx). 
    
    Args:
        - ???
    
    """
    
    # set logging; suppress logging by default. 
    logging.basicConfig(level=logging.DEBUG)
    #logging = logging.getLogger(__name__)
    ##logging.addHandler(logging.NullHandler())
    
    # ???
    RDF = []
    ns_prefix = "rdf"
    ns_map = rdf_dc_ns

    # ???
    logging.info("Opening workbook '{}'.".format(xlsx_path))
    # do try/except here and log if you can't open the file.
    workbook = load_workbook(xlsx_path, read_only=False, data_only=True)
    worksheets = workbook.get_sheet_names()

    # create instance of generic element builder.
    make = AnyType(ns_prefix, ns_map).anyType

    for worksheet in worksheets:
        
        logging.info("Looking for metadata in worksheet '{}'.".format(worksheet))
        worksheet_object = workbook[worksheet]
        header_map = [(header.value, header.column) for header in worksheet_object[1:1]]
        header_map = dict(header_map)
        logging.debug("Found headers: {}".format(header_map))
        
        # ???
        if element_header not in header_map.keys():
            logging.info("Skipping worksheet. Missing required header '{}'.".format(
                element_header))
            continue
        elif value_header not in header_map.keys():
            logging.info("Skipping sheet. Missing required header '{}.'".format(
                value_header))
            continue
        else: 
            logging.info("Success. Found required headers.".format(element_header,
                value_header))

        # ???
        metadata = []
        for header in [element_header, value_header]:
            header_column = header_map[header]
            column = [cell.value for cell in worksheet_object[header_column][1:]]
            metadata.append(column)

        # ??? paranoid check.
        elements, values = metadata[0], metadata[1]
        if not len(elements) == len(values):
            logging.warning("Skipping sheet. Length of '{}' and '{}' do not match.".format(
                element_header, value_header))
            continue

        # ???
        rdf_id = "{}".format(metadata) + datetime.utcnow().isoformat()
        rdf_id = rdf_id.encode("utf-8")
        logging.debug("Unhashed metadata + timestamp: {}".format(rdf_id))  
        rdf_id = "_" + hashlib.sha256(rdf_id).hexdigest()
        logging.debug("Hashed metadata + timestamp: {}".format(rdf_id))        
            
        # ???
        rdf_root = make("rdf:RDF")
        rdf_description = make("rdf:Description", {"rdf:ID":rdf_id})
        for i in range(0, len(elements)):
            element, value = elements[i], values[i]
            if element is not None and value is not None:
                element = make("dc:" + element)
                element.text = str(value)
                rdf_description.append(element)
            rdf_root.append(rdf_description)
        logging.info("RDF tree built.")
        RDF.append(rdf_root)

    return RDF

if __name__ == "__main__":
    r = excel_to_rdf("test.xlsx")
    print()
    print("Here are any RDF trees that were created ...")

    for i in r:
        print()
        s = (etree.tostring(i, pretty_print=True))
        s = s.decode("utf-8")
        print(s)

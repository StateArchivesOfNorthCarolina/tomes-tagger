#!/usr/bin/env python3

"""
This module creates a METS <fileGrp> tree for a given list of files. The output can be
integrated into a complete METS file's <fileSec> element.

TODO:
    - Might need a separate <fileGrp> element for preservation EAXS vs. tagged. This can wait
    until our AIP structure is solid. It's really up to the Archivists. Also, the <fileGrp>
    @USE attribute might be something they want too.
"""

# import modules.
import hashlib
import mets_ns
import mimetypes
import os
from datetime import datetime
from lxml import etree


# to save <file> ID attributes.
fileGrp_ids = []


def fileGrp(filenames, basepath, identifier, attributes=None):
    """ Creates a METS <fileGrp> etree element for all files in @filenames.

    Args:
        - filenames (list): All filepaths from which to create a <fileGrp> element.
        - basepath (str): Each <file> element's <FLocat> value is relative to this path.
        - identifier (str): The ID attribute value to set for the <fileGrp>.
        - attributes (dict): The optional attributes to set for the <fileGrp>.
    
    Returns:
        <class 'lxml.etree._Element'>
    """
    
    # create <fileGrp> element for current directory; set ID and optional attributes.
    fileGrp_el = etree.Element(mets_ns.ns_id("mets") +  "fileGrp", nsmap=mets_ns.ns_map)
    if attributes is not None:
        for k, v in attributes.items():
            fileGrp_el.set(k, v)
    fileGrp_el.set("ID", identifier)

    i = 0
    for filename in filenames:  

        # create <file> element for current file; set easy attributes.
        file_el = etree.SubElement(fileGrp_el, mets_ns.ns_id("mets") +  "file", nsmap=mets_ns.ns_map)
        file_el.set("CHECKSUMTYPE", "SHA-256")
        file_el.set("SIZE", str(os.path.getsize(filename)))

        # set ID attribute; update list of ids.
        filename_id = identifier + "_" + str(i).zfill(6)
        file_el.set("ID", filename_id)
        fileGrp_ids.append(filename_id)
        
        # set MIMETYPE attribute.
        mime = mimetypes.guess_type(filename)[0]
        if mime is not None:
            file_el.set("MIMETYPE", mime)
        
        # set CHECKSUM attribute.
        with open(filename, "rb") as f:
            fb = f.read()
            checksum = hashlib.sha256(fb)
            checksum = checksum.hexdigest()
            file_el.set("CHECKSUM", checksum)

        # set CREATED attribute.
        file_created = os.path.getctime(filename)
        file_created = datetime.utcfromtimestamp(file_created).isoformat()
        file_el.set("CREATED", file_created)

        # create <FLocat> element; set attributes.
        filename = os.path.relpath(filename, basepath)
        filename = filename.replace("\\", "/")
        flocat_el = etree.SubElement(file_el, mets_ns.ns_id("mets") +  "FLocat", nsmap=mets_ns.ns_map)
        flocat_el.set(mets_ns.ns_id("xlink") + "href", filename)
        flocat_el.set("LOCTYPE", "OTHER")
        flocat_el.set("OTHERLOCTYPE", "SYSTEM")
    
        i += 1

    return fileGrp_el


# TEST.
def main():

    from glob import glob

    # create <fileGrp> based on @path.
    path = "."
    files = glob(path + "/**/*.*", recursive=True)
    attribs = {"USE": "Testing"}
    groupx = fileGrp(files, path, "ID_fileGrp", attribs)
    return(groupx)


if __name__ == "__main__":
    
    groupx = main()

    # print XML.
    groupx = etree.tostring(groupx, pretty_print=True)
    groupx = groupx.decode("utf-8")
    print(groupx)

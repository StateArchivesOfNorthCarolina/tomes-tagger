#!/usr/bin/env python3

"""
This module creates a METS <fileGrp> tree for a given list of files. The output can be
integrated into a complete METS file.

TODO:
    - Might need a separate <fileGrp> element for preservation EAXS vs. tagged. This can wait
    until our AIP structure is solid. It's really up to the Archivists. Also, the <fileGrp>
    @USE attribute might be something they want too.
        - This will now go into the master class because this module will only return
        <fileGrp> elements.
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


def fileGrp(filenames, basepath, identifier):
    """ Creates METS <fileGrp> for all files in @filenames.

    Args:
        - filenames: list
        - basepath: str
        - identifier: str
    
    Returns:
        <class 'lxml.etree._Element'>.
    """
    
    # create <fileGrp> element for current directory.
    fileGrp_el = etree.Element(mets_ns.ns_id + "fileGrp", nsmap=mets_ns.ns_map)
    fileGrp_el.set("ID", identifier)

    i = 0
    for filename in filenames:  

        # create <file> element for current file; set easy attributes.
        file_el = etree.SubElement(fileGrp_el, mets_ns.ns_id + "file", nsmap=mets_ns.ns_map)
        file_el.set("CHECKSUMTYPE", "SHA-256")
        file_el.set("SIZE", str(os.path.getsize(filename)))

        # set ID attrbute.
        filename_id = "file_" + str(i).zfill(7)
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

        # create <FLocat> element; set LOCTYPE attribute.
        flocat_el = etree.SubElement(file_el, mets_ns.ns_id + "FLocat", nsmap=mets_ns.ns_map)
        flocat_el.set("LOCTYPE", "OTHER")
        filename = os.path.relpath(filename, basepath)
        filename = filename.replace("\\", "/")
        flocat_el.text = etree.CDATA(filename)

        i += 1

    return fileGrp_el


# TEST.
def main(path):

    # create <fileGrp> based on @path.
    from glob import glob
    files = glob(path + "/**/*.*", recursive=True)
    group = fileGrp(files, path, "test")

    # print XML.
    groupx = etree.tostring(group, pretty_print=True)
    groupx = groupx.decode("utf-8")
    print(groupx)

    # print list of <file> @ID attributes.
    ids = fileGrp_ids
    ids = "<!--" + str(ids) + "-->"
    print(ids)

if __name__ == "__main__":
    
    import plac
    plac.call(main)


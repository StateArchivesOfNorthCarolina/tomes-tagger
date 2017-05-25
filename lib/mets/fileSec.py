#!/usr/bin/env python3

"""
This module creates a METS <fileSec> tree for a given user-inputted path. The output can be
integrated into a complete METS file.

Usage:
    >>> import fileSec
    >>> mets_fileSec = fileSec.make("./myDir") # etree <fileSec> element.
    >>> mets_fileSec_ids = fileSec.file_ids # list of <file> element @ID attributes.

TODO:
    - Might need a separate <fileGrp> element for preservation EAXS vs. tagged. This can wait until
    our AIP structure is solid. It's realy up to the Archivists.
    - Also, the <fileGrp> @USE attribute might be something they want too.
"""

# import modules.
import mets
import mimetypes
import os
from datetime import datetime
from hashlib import sha1, sha256
from lxml import etree


# to save <file> ID attributes.
file_ids = []


def make(filepath):
    """ Returns METS <fileSec> for all files in @filepath.
    Return type is <class 'lxml.etree._Element'>. """
    
    i = 0

    # create root <fileSec> element.
    fileSec_el = etree.Element(mets.ns_id + "fileSec", nsmap=mets.ns_map)

    # loop through subdirectories and files.
    for dirpath, dirnames, filenames in os.walk(filepath):
        
        # get current relative path; replace Windows backslashes.
        relative_path = os.path.relpath(dirpath, filepath)
        relative_path = relative_path.replace("\\", "/")
        
        # create <fileGrp> element for current directory.
        fileGrp_el = etree.SubElement(fileSec_el, mets.ns_id + "fileGrp", nsmap=mets.ns_map)
        relative_path_bytes = bytes(relative_path, encoding="utf-8")
        fileGrp_id = sha1(relative_path_bytes).hexdigest()
        fileGrp_el.set("ID", fileGrp_id)

        for filename in filenames:  

            # create full path to file.
            fullname = os.path.join(dirpath, filename)

            # create <file> element for current file; set easy attributes.
            file_el = etree.SubElement(fileGrp_el, mets.ns_id + "file", nsmap=mets.ns_map)
            file_el.set("CHECKSUMTYPE", "SHA-256")
            file_el.set("SIZE", str(os.path.getsize(fullname)))

            # set ID attrbute.
            filename_id = "file_" + str(i).zfill(7)
            file_el.set("ID", filename_id)
            file_ids.append(filename_id)
            
            # set MIMETYPE attribute.
            mime = mimetypes.guess_type(fullname)[0]
            if mime is not None:
                file_el.set("MIMETYPE", mime)
            
            # set CHECKSUM attribute.
            with open(fullname, "rb") as f:
                checksum = sha256(f.read()).hexdigest()
                file_el.set("CHECKSUM", checksum)

            # set CREATED attribute.
            file_created = os.path.getctime(fullname)
            file_created = datetime.utcfromtimestamp(file_created).isoformat()
            file_el.set("CREATED", file_created)

            # create <FLocat> element; set LOCTYPE attribute.
            flocat_el = etree.SubElement(file_el, mets.ns_id + "FLocat", nsmap=mets.ns_map)
            flocat_el.set("LOCTYPE", "OTHER")
            flocat_el.text = etree.CDATA(relative_path + "/" + filename)

            i += 1

    return fileSec_el


# TEST.
def main(path):

    # create <fileSec> based on @path.
    fileSec = make(path)

    # print XML.
    fileSec = etree.tostring(fileSec, pretty_print=True)
    fileSec = fileSec.decode("utf-8")
    print(fileSec)

    # print list of <file> @ID attributes.
    print(file_ids)

if __name__ == "__main__":
    
    import plac
    plac.call(main)


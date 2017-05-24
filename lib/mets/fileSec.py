"""
usage:
    >>> make_fileSec("./myDir")
"""

# import modules.
import hashlib
import mimetypes
import os
from datetime import datetime
from lxml import etree

# set namespace prefixes.
ns_url = "http://www.loc.gov/METS/" # get this from an external source eventually OR when inhereted.
ns_dir_id = "{" + ns_url + "}"
ns_map = {None : ns_url}


def make_fileSec(filepath):
    """ Returns METS <fileSec> for all files in @filepath.
    Return type is <class 'lxml.etree._Element'>. """

    # create root <fileSec> element.
    fileSec_el = etree.Element(ns_dir_id + "fileSec", nsmap=ns_map)

    # loop through subdirectories and files.
    for dirpath, dirnames, filenames in os.walk(filepath):
        
        # get current relative path; replace Windows backslashes.
        dir_id = os.path.relpath(dirpath, filepath)
        dir_id = dir_id.replace("\\", "/")
        
        # create <fileGrp> element for current directory.
        fileGrp_el = etree.SubElement(fileSec_el, ns_dir_id + "fileGrp", nsmap=ns_map)
        fileGrp_el.set("ID", dir_id)

        for filename in filenames:  

            # create full path to file.
            fullname = os.path.join(dirpath, filename)

            # create <file> element for current file; set easy attributes.
            file_el = etree.SubElement(fileGrp_el, ns_dir_id + "file", nsmap=ns_map)
            file_el.set("CHECKSUMTYPE", "SHA-256")
            file_el.set("SIZE", str(os.path.getsize(fullname)))

            # set MIMETYPE attribute.
            mime = mimetypes.guess_type(fullname)[0]
            if mime is not None:
                file_el.set("MIMETYPE", mime)
            
            # set CHECKSUM attribute.
            with open(fullname, "rb") as f:
                checksum = hashlib.sha256()
                checksum.update(f.read())
                file_el.set("CHECKSUM", checksum.hexdigest())

            # set CREATED attribute.
            file_created = os.path.getctime(fullname)
            file_created = datetime.utcfromtimestamp(file_created).isoformat()
            file_el.set("CREATED", file_created)

            # create <FLocat> element; set LOCTYPE attribute.
            flocat_el = etree.SubElement(file_el, ns_dir_id + "FLocat", nsmap=ns_map)
            flocat_el.set("LOCTYPE", "OTHER")
            flocat_el.text = filename

    return fileSec_el


# TEST.
testDir = open(".testDir").read()
fileSec = make_fileSec(testDir)
fileSec = etree.tostring(fileSec, pretty_print=True)
fileSec = fileSec.decode("utf-8")
print(fileSec)


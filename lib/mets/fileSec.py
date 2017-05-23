"""
attachments = fileSec.fileGrp("./myDir", "attachments")
"""

#
import hashlib
import os
from datetime import datetime
from lxml import etree

#
def get_mime(f):
    mimes = {".xml": "application/xml"}
    ext = os.path.splitext(f)[1]
    mime = mimes.get(ext)
    return mime
    
#
def fileGrp(directory, suffix):

    ns_url = "http://www.loc.gov/METS/" # get this from an external source eventually OR when inhereted.
    ns_prefix = "{" + ns_url + "}"
    ns_map = {"METS" : ns_url}
    
    i = 0
    #fileGrp = []
    fileGrp_el = etree.Element(ns_prefix + "fileGrp", nsmap=ns_map)
    fileGrp_el.set("ID", suffix)
    for root, dirs, files in os.walk(directory + "/" + suffix):
        
        for myfile in files:

            myfile = os.path.join(root, myfile)

            file_el = etree.SubElement(fileGrp_el, ns_prefix + "file", nsmap=ns_map)

            file_el.set("ID", suffix + "_" + str(i).zfill(5))
            file_el.set("CHECKSUMTYPE", "SHA-256")
            file_el.set("MIMETYPE", get_mime(myfile))
            file_el.set("SIZE", str(os.path.getsize(myfile)))
            with open(myfile, "rb") as f:
                checksum = hashlib.sha256()
                checksum.update(f.read())
                file_el.set("CHECKSUM", checksum.hexdigest())

            # "The number of seconds can include decimal digits to arbitrary precision." per: https://www.w3.org/TR/xmlschema-2/
            file_created = os.path.getctime(myfile)
            file_created = datetime.utcfromtimestamp(file_created).isoformat()
            file_el.set("CREATED", file_created)

            flocat_el = etree.SubElement(file_el, ns_prefix + "FLocat", nsmap=ns_map)
            flocat_el.set("LOCTYPE", "OTHER")
            flocat_el.text = myfile.replace(directory, "")
            flocat_el.text = flocat_el.text.replace("\\", "/")

            i += 1
            if i == 5:
                break

        return fileGrp_el
   
testDir = open(".testDir").read()
results = fileGrp(testDir, "attachments")
xml = etree.tostring(results, pretty_print=True)
print(xml.decode("utf-8"))

#!/usr/bin/env python3

""" This module contains a class to create a METS <fileGrp> tree for a given list of files.
The output can be integrated into a complete METS file's <fileSec> element."""

# import modules.
import hashlib
import mimetypes
import os
from datetime import datetime
from lxml import etree


class FileGrp():
    """ A class to create a METS <fileGrp> tree for a given list of files. The output can be
    integrated into a complete METS file's <fileSec> element. """


    def __init__(self, ns_prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        self.ns_prefix = ns_prefix
        self.ns_map = ns_map


    def fileGrp(self, filenames, basepath, identifier, attributes=None):
        """ Creates a METS <fileGrp> element for all files in @filenames.

        Args:
            - filenames (list): The file paths from which to create a <fileGrp> element.
            - basepath (str): Each <file> element's <FLocat> value is relative to this path.
            - identifier (str): The ID attribute value to set.
            - attributes (dict): The optional attributes to set.
        
        Returns:
            lxml.etree._Element: The return value.
        """

        # create <fileGrp> element.
        fileGrp_el = etree.Element("{" + self.ns_map[self.ns_prefix] + "}fileGrp",
                nsmap=self.ns_map)
       
        # set optional attributes and ID attribute.
        if attributes is not None:
            for k, v in attributes.items():
                fileGrp_el.set(k, v)
        fileGrp_el.set("ID", identifier)

        # add a sub-element for each file.
        i = 0
        for filename in filenames:  

            # create <file> element.
            file_el = etree.SubElement(fileGrp_el, "{" + self.ns_map[self.ns_prefix] +
                    "}file", nsmap=self.ns_map)
            
            # set simple attributes.
            file_el.set("CHECKSUMTYPE", "SHA-256")
            file_size = os.path.getsize(filename) # get file size.
            file_el.set("SIZE", str(file_size))
            filename_id = identifier + "_" + str(i).zfill(6) # make ID string.
            file_el.set("ID", filename_id)
            
            # get mimetype; set MIMETYPE attribute.
            mime = mimetypes.guess_type(filename)[0]
            if mime is not None:
                file_el.set("MIMETYPE", mime)
            
            # get checksum; set CHECKSUM attribute.
            with open(filename, "rb") as f:
                fb = f.read()
                checksum = hashlib.sha256(fb)
                checksum = checksum.hexdigest()
                file_el.set("CHECKSUM", checksum)

            # get file creation date; set CREATED attribute.
            file_created = os.path.getctime(filename)
            file_created = datetime.utcfromtimestamp(file_created).isoformat()
            file_el.set("CREATED", file_created)

            # create <FLocat> element; set attributes.
            filename = os.path.relpath(filename, basepath)
            filename = filename.replace("\\", "/")
            flocat_el = etree.SubElement(file_el, "{" + self.ns_map[self.ns_prefix] +
                    "}FLocat", nsmap=self.ns_map)
            flocat_el.set("{" + self.ns_map["xlink"] + "}href", filename)
            flocat_el.set("LOCTYPE", "OTHER")
            flocat_el.set("OTHERLOCTYPE", "SYSTEM")
        
            i += 1

        return fileGrp_el


if __name__ == "__main__":
    pass


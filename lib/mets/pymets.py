#!/usr/bin/env python3

"""
TODO:
    - Note that struct-links and behavior elements aren't supported.
    - Say this is for METS version 1.11.
    - Get rid of "text" arg in AnyType and here. Just use etree's text attribute.
    - Add a load() method to load XML strings.
"""

# import modules.
from lxml import etree
from lxml.etree import CDATA
from lxml.etree import Comment
from lib.anyType import AnyType
from lib.div import Div
from lib.fileGrp import FileGrp
import lib.namespaces as namespaces


class PyMETS():
    """ A class with covenience methods for creating METS files. """

    
    def __init__(self, ns_prefix="mets", ns_map=namespaces.mets_ns):
        """ Set instance attributes.

        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """

        self.ns_prefix = ns_prefix
        self.ns_map = ns_map

        # compose instances.
        self.AnyType = AnyType(self.ns_prefix, self.ns_map)
        self.Div = Div(self.ns_prefix, self.ns_map)
        self.FileGrp = FileGrp(self.ns_prefix, self.ns_map)


    def stringify(self, element, beautify=True, charset="utf-8"):
        """ Returns an XML string for a given etree @element. """

        xstring = etree.tostring(element, pretty_print=beautify)
        xstring = xstring.decode(charset)
        return xstring


    def make(self, *args, **kwargs):
        """ Returns an etree element using the self.AnyType instance. """

        name_el = self.AnyType.anyType(*args, **kwargs)
        return name_el


    def div(self, *args, **kwargs):
        """ Returns a METS <div> etree element using the self.Div instance. """

        div_el = self.Div.div(*args, **kwargs)
        return div_el


    def fileGrp(self, *args, **kwargs):
        """ Returns a METS <fileGrp> etree element using the self.FileGrp instance. """

        filegrp_el = self.FileGrp.fileGrp(*args, **kwargs)
        return filegrp_el


# TEST.
def main():
    
    pymets = PyMETS()
    
    # create METS root; set <metsHdr>; append header to root.
    root = pymets.make("mets")
    header = pymets.make("metsHdr")
    root.append(header)
    
    # create <agent>; append to header.
    attributes = {"ROLE":"CREATOR", "TYPE":"OTHER",  "OTHERTYPE":"Software Agent"}
    agent = pymets.make("agent", attributes=attributes)
    name = pymets.make("name")
    name.text = "TOMES Tool"
    note = pymets.make("note")
    note.text = CDATA("TOMES Tool is written in Python.")
    agent.extend([name, note])
    agent.append(Comment("This is a comment!"))
    header.append(agent)
    
    # create <dmdSec>.
    dmdSec = pymets.make("dmdSec", attributes={"ID":"no_metadata"})
    root.append(dmdSec)
    
    # create <fileSec>.
    fileSec = pymets.make("fileSec")
    fileGrp = pymets.fileGrp(filenames=[__file__], basepath=".", identifier="source_code")
    fileSec.append(fileGrp)
    root.append(fileSec)

    # create <div>; create <structMap>.
    file_ids = [fid.get("ID") for fid in fileGrp.findall("{*}file")]
    structMap = pymets.make("structMap")
    div = pymets.div(file_ids)
    structMap.append(div)
    root.append(structMap)

    # print METS.
    rootx = pymets.stringify(root)
    print(rootx)


if __name__ == "__main__":
    main()

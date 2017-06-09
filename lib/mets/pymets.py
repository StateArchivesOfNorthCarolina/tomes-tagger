#!/usr/bin/env python3

"""
TODO:
    - Note that struct-links and behavior elements aren't supported.
    - Say this is for METS version 1.11.
        - Doesn't the default for @xsd already tell me that?
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

    
    def __init__(self, ns_prefix="mets", ns_map=namespaces.mets_ns,
            xsd="mets_version_1-11.xsd"):
        """ Set instance attributes.

        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
            - xsd (str): The filepath for the METS XSD.
        """

        self.ns_prefix = ns_prefix
        self.ns_map = ns_map
        self.xsd = xsd

        # compose instances.
        self.AnyType = AnyType(self.ns_prefix, self.ns_map)
        self.Div = Div(self.ns_prefix, self.ns_map)
        self.FileGrp = FileGrp(self.ns_prefix, self.ns_map)


    def load(self, xml, is_string=False):
        """ Returns etree element for an XML file or XML string (@is_string==True). """
        
        if is_string:
            x_el = etree.fromstring(xml)
        else:
            x_el = etree.parse(xml).getroot()
        return x_el


    def stringify(self, element, beautify=True, charset="utf-8"):
        """ Returns XML as string for a given etree @element. """

        xstring = etree.tostring(element, pretty_print=beautify)
        xstring = xstring.decode(charset)
        return xstring


    def valid(self, xdoc):
        """ Returns boolean for "Is @xdoc valid against self.xsd?". """
        
        xsd = self.load(self.xsd)
        xsd = etree.XMLSchema(xsd)
        valid = xsd.validate(xdoc)
        return valid


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
    
    # create METS root.
    root = pymets.make("mets")
    
    # create <metsHdr>; append to root.
    header = pymets.make("metsHdr")
    root.append(header)
    
    # create header <agent>.
    attributes = {"ROLE":"CREATOR", "TYPE":"OTHER",  "OTHERTYPE":"Software Agent"}
    agent = pymets.make("agent", attributes=attributes)
    header.append(agent)
    name = pymets.make("name")
    name.text = "TOMES Tool"
    agent.append(name)

    # create <fileSec>.
    fileSec = pymets.make("fileSec")
    fileGrp = pymets.fileGrp(filenames=[__file__], basepath=".", identifier="source_code")
    fileSec.append(fileGrp)
    root.append(fileSec)

    # create <structMap> and <div>.
    structMap = pymets.make("structMap")
    file_ids = [fid.get("ID") for fid in fileGrp.findall("{*}file")]
    div = pymets.div(file_ids)
    structMap.append(div)
    root.append(structMap)

    # append valid() response to root as comment.
    valid = pymets.valid(root)
    valid = "It is {} that this METS document is valid.".format(valid)
    root.append(Comment(valid))

    # print METS.
    rootx = pymets.stringify(root)
    print(rootx)


if __name__ == "__main__":
    main()

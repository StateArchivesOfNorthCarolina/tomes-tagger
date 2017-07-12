#!/usr/bin/env python3

"""
TODO:
    - Note that struct-links and behavior elements aren't supported.
    - Say this is for METS version 1.11.
        - Doesn't the default for @xsd already tell me that?
    - get_fileIDs() seems to be slowing things down. It seemed faster when I used the "*"
    instead of the specific METS namespace URI.
"""

# import modules.
import codecs
import os
from lxml import etree
from lib.anyType import AnyType
from lib.div import Div
from lib.fileGrp import FileGrp
import lib.namespaces as namespaces


class PyMETS():
    """ A class with covenience methods for creating METS files. """

    
    def __init__(self, ns_prefix="mets", ns_map=namespaces.mets_ns, xsd_file=None):
        """ Set instance attributes.

        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
            - xsd_file (str): The filepath for the METS XSD.
        """

        self.ns_prefix = ns_prefix
        self.ns_map = ns_map
        if xsd_file is None:
            xsd_file = os.path.split(os.path.abspath(__file__))[0] + "/mets_1-11.xsd"
        self.xsd_file = xsd_file
        self.cdata = etree.CDATA
        self.comment = etree.Comment

        # compose instances.
        self.AnyType = AnyType(self.ns_prefix, self.ns_map)
        self.Div = Div(self.ns_prefix, self.ns_map)
        self.FileGrp = FileGrp(self.ns_prefix, self.ns_map)


    def load(self, xml, is_raw=True):
        """ Returns etree element for an XML file or XML string (@is_raw==True). """
        
        #
        parser = etree.XMLParser(remove_blank_text=True)
        
        #
        if is_raw:
            loaded_el = etree.fromstring(xml, parser)
        else:
            loaded_el = etree.parse(xml, parser).getroot()
        
        return loaded_el


    def load_template(self, xml, charset="utf-8", *args, **kwargs):
        """ Returns etree element for an XML string after formatting the string using the
        string.Formatter.format() method for @args and @kwargs. """

        #
        with codecs.open(xml, encoding=charset) as xfile:
            xstring = xfile.read().format(*args, **kwargs)
        
        template_el = self.load(xstring)
        return template_el


    def stringify(self, element, beautify=True, charset="utf-8"):
        """ Returns XML as string for a given etree @element. """

        #
        xstring = etree.tostring(element, pretty_print=beautify)
        xstring = xstring.decode(charset)
        
        return xstring


    def valid(self, xdoc):
        """ Returns boolean for "Is @xdoc valid against self.xsd?". """
        
        #
        xsd = self.load(self.xsd_file, False)
        validator = etree.XMLSchema(xsd)
        
        #
        is_valid = validator.validate(xdoc)
        return is_valid


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


    def get_fileIDs(self, file_el):
        """ Returns a list of <fileGrp/file[@ID]> values for a given @file_el which can be an
        individual <fileGrp> etree element or and entire <fileSec> etree element."""

        #
        path = "{" + self.ns_map[self.ns_prefix] + "}file"

        #
        if file_el.tag[-7:] == "fileSec":
            path = "*" + path
        
        fids = [fid.get("ID") for fid in file_el.findall(path)]
        return fids


    def wrap(self, xtree, mdtype, attributes={}, xmlData=True):
        """ Returns <mdWrap> etree element with "MDTYPE" attribute of @mdtype and
        optional @attributes. The @xtree etree element will have a parent element of
        <xmlData> (@xmlData==True) or <binData>. """
        
        #
        attributes["MDTYPE"] = mdtype
        wrap_el = self.make("mdWrap", attributes)

        #
        if xmlData:
            xobdata_el = self.make("xmlData")
        else:
            xobdata_el = self.make("binData")
        
        #
        xobdata_el.append(xtree)
        wrap_el.append(xobdata_el)
        
        return wrap_el
        

if __name__ == "__main__":
    pass


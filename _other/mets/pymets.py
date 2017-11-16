#!/usr/bin/env python3

"""
This module contains a class with covenience methods for creating METS files.

Todo:
    * Note that struct-links and behavior elements aren't supported.
    * Say this is for METS version 1.11.
        - Doesn't the default for @xsd already tell me that?
    * get_fileIDs() seems to be slowing things down. It seemed faster when I used the "*"
    instead of the specific METS namespace URI.
    * Do you want to add a base64 convenience method to help wrap a <binData> value?
"""

# import modules.
import codecs
import os
from lxml import etree
from lib import anyType
from lib import div
from lib import fileGrp
from lib import namespaces


class PyMETS():
    """ A class with covenience methods for creating METS files.
    
    Example:
    >>> pymets = PyMETS()
    >>> root = pymets.make("mets") # create METS root.
    >>> header = pymets.make("metsHdr")
    >>> root.append(header)
    >>> attributes = {"ROLE":"CREATOR", "TYPE":"OTHER",  "OTHERTYPE":"Software Agent"}
    >>> agent = pymets.make("agent", attributes=attributes)
    >>> header.append(agent)
    >>> name = pymets.make("name")
    >>> name.text = "PyMETS"
    >>> agent.append(name)
    >>> pymets.stringify(root) # string version of METS.
    '<mets:mets xmlns:mets="http://www.loc.gov/METS/"
    ...
    </mets:mets>\n'
    >>> pymets.validate(root) # Not valid due to missing <StructMap>, etc.
    False
    """

    
    def __init__(self, ns_prefix="mets", ns_map=namespaces.mets_ns, xsd_file=None):
        """ Sets instance attributes.

        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
            This must at least contain an item where @ns_prefix is the key.
            - xsd_file (str): The filepath for the METS XSD.
        """

        # set attributes.
        self.ns_prefix = ns_prefix
        self.ns_map = ns_map

        # use default XSD if none provided.
        if xsd_file is None:
            xsd_file = os.path.split(os.path.abspath(__file__))[0] + "/mets_1-11.xsd"
        self.xsd_file = xsd_file
        
        # get functions for writing CDATA blocks and XML comments.
        self.CDATA = etree.CDATA
        self.Comment = etree.Comment

        # compose instances of helper classes.
        self.AnyType = anyType.AnyType(self.ns_prefix, self.ns_map)
        self.Div = div.Div(self.ns_prefix, self.ns_map)
        self.FileGrp = fileGrp.FileGrp(self.ns_prefix, self.ns_map)


    def load(self, xml, is_raw=False):
        """ Loads @xml file or XML string (@is_raw==True) as lxml.etree._Element.
        
        Args:
            - xml (str): The file or string to load.
            - is_raw (bool): Use True to load a string, False to load a file.
            
        Returns:
            lxml.etree._Element: The return value.
        """
        
        # set custom parser.
        parser = etree.XMLParser(remove_blank_text=True)
        
        # load string or file as needed.
        if is_raw:
            loaded_el = etree.fromstring(xml, parser)
        else:
            loaded_el = etree.parse(xml, parser).getroot()
        
        return loaded_el


    def load_template(self, xml, charset="utf-8", *args, **kwargs):
        """ Loads an @xml string after formatting the string using the
        string.Formatter.format() with for *args and **kwargs.
        
        Args:
            - xml (str): The file to load.
            - charset (str): The optional encoding with which to load the file.
            - *args/**kwargs: The optional arguments to pass to the string formatter.
            
        Returns:
            lxml.etree._Element: The return value.
        """

        # read file as string; format it.
        with codecs.open(xml, encoding=charset) as xfile:
            xstring = xfile.read().format(*args, **kwargs)
        
        # load string.
        template_el = self.load(xstring, is_raw=True)
        return template_el


    def stringify(self, element, beautify=True, charset="utf-8"):
        """ Returns a string version for a given XML @element.
        
        Args:
            - element (lxml.etree._Element):
            - beautify (bool): Use True to pretty print.
            - charset (str): The character encoding for the returned string.

        Returns:
            str: The return value.
        """

        xstring = etree.tostring(element, pretty_print=beautify)
        xstring = xstring.decode(charset)
        
        return xstring


    def validate(self, xdoc):
        """ Validates @xdoc file against METS XSD.
        
        Args:
            - xdoc (str): The file to validate.
            
        Returns:
            bool: The return value. True for valid, otherwise False.
        """
        
        # load XSD.
        xsd = self.load(self.xsd_file, False)
        validator = etree.XMLSchema(xsd)
        
        # validate.
        is_valid = validator.validate(xdoc)
        return is_valid


    def make(self, *args, **kwargs):
        """ Returns an etree element using the self.AnyType instance.
        
        Returns:
            lxml.etree._Element: The return value.
        """

        name_el = self.AnyType.anyType(*args, **kwargs)
        return name_el


    def div(self, *args, **kwargs):
        """ Returns a METS <div> etree element using the self.Div instance.

        Returns:
            lxml.etree._Element: The return value.
        """

        div_el = self.Div.div(*args, **kwargs)
        return div_el


    def fileGrp(self, *args, **kwargs):
        """ Returns a METS <fileGrp> etree element using the self.FileGrp instance.
        
        Returns:
            lxml.etree._Element: The return value.
        """

        filegrp_el = self.FileGrp.fileGrp(*args, **kwargs)
        return filegrp_el


    def get_fileIDs(self, file_el):
        """ Returns a list of <fileGrp/file> @ID values for a given @file_el - an individual
        <fileGrp> or an entire <fileSec> element.
        
        Args:
            - @file_el (lxml.etree._Element): A <fileGrp> or <fileSec> lxml.etree._Element.
            
        Returns:
            list: The return value.
        """

        # set <file> path.
        path = "{" + self.ns_map[self.ns_prefix] + "}file"

        # make adjustments if @file_el is a <fileSec> element.
        if file_el.tag[-7:] == "fileSec":
            path = "*" + path
        
        # make list of @ID attributes.
        fids = [fid.get("ID") for fid in file_el.findall(path)]
        return fids


    def wrap(self, xtree, mdtype, attributes={}, xmlData=True):
        """ Wraps etree element (@xtree) in an <mdWrap/xmlData|binData> etree element.
        
        Args:
            - xtree (lxml.etree._Element): An etree XML element.
            - mdtype (str): The required "MDTYPE" attribute for the <mdWrap> element.
            - attributes (dict): The optional attributes to set.
            - xmlData (bool): Use True to wrap @xtree within a parent <xmlData> element.
            Use false to wrap a parent <binData> element.
            
        Returns:
            lxml.etree._Element: The return value.
        """
        
        # add/overwrite @mdtype to attributes; make root element.
        attributes["MDTYPE"] = mdtype
        wrap_el = self.make("mdWrap", attributes)

        # set parent for @xtree.
        if xmlData:
            xobdata_el = self.make("xmlData")
        else:
            xobdata_el = self.make("binData")
        
        # wrap @xtree.
        xobdata_el.append(xtree)
        wrap_el.append(xobdata_el)
        
        return wrap_el
        

if __name__ == "__main__":
    pass


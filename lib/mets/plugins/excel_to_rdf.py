#!/usr/bin/env python3

"""
This module contains a class for creating RDF/Dublin Core metadata from a Microsoft Excel 2010
file (.xlsx).

Todo:
    *
"""

'''
Since plugins can import from lib, add RDF NS to namespaces.py.

Ex:

<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
xmlns:dc="http://purl.org/dc/elements/1.1/">
	<rdf:Description rdf:ID="_7a907b7c800b42794a4fe46d718a7ee144979dc54baf688bfb51abdf214c076f">
		<dc:title>TOMES Guy email correspondence.</dc:title>
		<dc:creator>Nitin Arora</dc:creator>
		<dc:creator>NCDCR</dc:creator>
		<dc:creator>State of North Carolina</dc:creator>
		<dc:date>20170101</dc:date>
	</rdf:Description>
</rdf:RDF> 

# about VS ID ...
from urllib import parse
if parse.urlparse("//foo").scheme == "":
    # use @rdf:ID
else:
    # use @rdf:about
'''

# import modules.
from lxml import etree


class ExcelToRDF():
    """ A class for creating RDF/Dublin Core metadata from a Microsoft Excel 2010 file 
    (.xlsx)."""

    
    def __init__(self,):
        pass


    def get_excel_files(self, path):
        pass



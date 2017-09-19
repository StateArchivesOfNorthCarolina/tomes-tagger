#!/usr/bin/env python3

"""
This module ... ???

Todo:
    * ???

"""

# import modules.
import csv
import logging
import os
from openpyxl import load_workbook


class EXCELToSTANFORD):
    """ A class for ... ??? """


    def __init__(self, pattern_header="pattern", case_header="case_sensitive", 
            label_header="label", authority_header="authority", charset="utf-8"):
        """ Sets instance attributes. """
        
        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler()

        # ???
        self.patter_header = patter_header
        self.case_header = case_header
        self.label_header = label_header
        self.authority_header = authority_header
        self.charset = charset


    def _get_regex_pattern(self, pattern, case_sensitive):
        """ ??? """

        # ???
        replacements = {"{abc}":".*[a-zA-Z]", "{123}":".*[0-9]", "{abc123}":".*[a-zA-Z0-9]"}
        for match, replacement in replacements.items():
            pattern = pattern.replace(match, replacement)

        # ???
        if case_sensitive:
            pattern = "(?i)" + " (?i)".join(pattern.split())

        return pattern


    def _get_worksheet_data(self, ):
        """ ??? """
        
        # can you convert "TRUE" to True/False here or does Excel library do that for me?
        return worksheet_data


    def filter_worksheets(self, worksheets):
        """ ??? """

        return worksheets


    def to_tsv(self, xslx_file, tsv_file=None):
        """ ??? """
        
        if os.path.isFile(tsv_file):
            self.logger()
            raise FileExistsError

        with open(tsv_file, "w") as tsv:
            for worksheet in self.filter_worksheets():
                worksheet_data = self._get_worksheet_data(worksheet):
                




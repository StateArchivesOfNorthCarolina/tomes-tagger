#!/usr/bin/env python3

"""
This module ... ???

Todo:
    * Do you need to handle/skip blank rows?
    * Can you assume the data is small enough to use a row list?

"""

# import modules.
import csv
import logging
import os
from openpyxl import load_workbook


class ExcelToStanford():
    """ A class for ... ??? """


    def __init__(self, pattern_header="pattern", case_header="case_sensitive", 
            label_header="label", authority_header="authority", charset="utf-8"):
        """ Sets instance attributes. """
        
        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # ???
        self.pattern_header = pattern_header
        self.case_header = case_header
        self.label_header = label_header
        self.authority_header = authority_header
        self.charset = charset


    def _get_pattern(self, pattern, case_sensitive):
        """ ??? """

        # ???
        if case_sensitive:
            pattern = "(?i)" + " (?i)".join(pattern.split())

        # ???
        replacements = {"{abc}":".*[a-zA-Z]", "{123}":".*[0-9]", "{abc123}":".*[a-zA-Z0-9]"}
        for match, replacement in replacements.items():
            pattern = pattern.replace("(?i)" + match, match)
            pattern = pattern.replace(match, replacement)


        return pattern


    def _get_worksheet_data(self, ):
        """ ??? """
        
        # ???
        return worksheet_data


    def filter_worksheets(self, xlsx_path):
        """ ??? """

        workbook = load_workbook(xlsx_path, read_only=False, data_only=True)
        worksheets = workbook.get_sheet_names()

        for worksheet in worksheets:
            if (self.pattern_header and 
                self.case_header and
                self.label_header and
                self.authority_header) not in worksheet:
                worksheets.remove(worksheet)
            
        return worksheets


    def to_tsv(self, xslx_file, tsv_file=None):
        """ ??? """
        
        # ???
        if os.path.isFile(tsv_file):
            err = "{} already exists.".format(tsv_file)
            self.logger.error(err)
            raise FileExistsError(err)

        # ???
        with open(tsv_file, "w") as tsv:
            tsv_writer = csv.writer(tsv, linetermator="")
            
            # ???; avoid trailing linebreak.
            # Note: Stanford CoreNLP will error if a mapping file contains a trailing linebreak.
            for worksheet in self.filter_worksheets():
                worksheet_rows = self._get_worksheet_rows(worksheet)
                for worksheet_row in worksheet_rows[-1]: # if you're using a generator, you can't do this!
                    tsv_writer.writerow(worksheet_row)
                    tsv.write("\n")
                tsv_writer.writerow(worksheet_rows[-1])

        return
                




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


class XLSXToStanford():
    """ A class for ... ??? """


    def __init__(self, entity_worksheet="Entities", charset="utf-8"):
        """ Sets instance attributes. """
        
        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # ???
        self.entity_worksheet = entity_worksheet
        
        # assume column number for required headers.
        self.required_headers = ("pattern", "description", "case_sensitive", "label", 
                "authority")


    def _interpret_pattern(self, pattern, is_case_sensitive):
        """ ??? """

        # ???
        if not is_case_sensitive:
            pattern = "(?i)" + " (?i)".join(pattern.split())

        # ???
        replacements = {"{abc}":".*[a-zA-Z]", "{123}":".*[0-9]", "{abc123}":".*[a-zA-Z0-9]"}
        for match, replacement in replacements.items():
            pattern = pattern.replace("(?i)" + match, match)
            pattern = pattern.replace(match, replacement)

        return pattern


    def _validate_header_row(self, header_row):
        """ ??? """
        
        # ???
        self.logger.info("Validating header row.")
        self.logger.debug("Found header row: {}".format(header_row))
        
        # ???
        if header_row == self.required_headers:
            self.logger.info("Header row is valid.")
            return True
        
        # ???
        missing_headers = [header for header in self.required_headers if header not in
                header_row]
        if len(missing_headers) != 0:
            missing_headers = ", ".join(missing_headers)
            self.logger.error("Header row is not valid. Missing: {}".format(missing_headers))
  
        return False


    def stanfordize_file(self, xlsx_file, tsv_file=None):
        """ ??? """
        
        # load workbook; verify that required worksheet exists.
        self.logger.info("Loading workbook: {}".format(xlsx_file))
        workbook = load_workbook(xlsx_file, read_only=False, data_only=True)
        try:
            rows = workbook[self.entity_worksheet]
        except KeyError:
            self.logger.error("Missing required worksheet '{}' in workbook: {}".format(
                    self.entity_worksheet, xlsx_file))
            raise
        
        # ???
        if tsv_file is not None:
            tsv_file = xlsx_file.replace(".xlsx", "__mapping.txt")
        if os.path.isfile(tsv_file):
            self.logger.warning("File '{}' already exists and will be overwritten.".format(
                tsv_file))
            
        # ???
        tsv = open(tsv_file, "w")
        tsv_writer = csv.writer(tsv, delimiter="\t", lineterminator="")
        
        #
        i = 1
        for row in rows.values:

            # validate headers.
            if i == 1:
                if not self._validate_header_row(row):
                    self.logger.info("Removing file: {}".format(tsv_file))
                    tsv.close()
                    os.remove(tsv_file)
                    err = "Bad header in workbook: {}".format(xlsx_file)
                    raise Exception(err)
                else:
                    self.logger.info("Writing to mapping file: {}".format(tsv_file))
            
            # write data to file.        
            else:
                if None in row:
                    self.logger.warning("Found empty cell in row {}. Skipping row.".format(i))
                    self.logger.debug("Row {}: {}".format(i, row))
                else:
                    pattern, description, case_sensitive, label, authority = row
                    pattern = self._interpret_pattern(pattern, case_sensitive)
                    label = authority + "/" + label
                    tsv_writer.writerow([pattern,label])

            # avoid final linebreak, otherwise CoreNLP will crash.
            if i != 1 and i != rows.max_row:
                tsv.write("\n")
            i += 1

        return


    def stanfordize_folder(self, input_dir, output_dir):
        """ ??? """
        pass


# TEST.
if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    xl_in = "../tests/sample_files/entity_dictionaries/foo.xlsx"
    xl_out = xl_in.replace(".xlsx", "_stanford.txt")

    x2s = XLSXToStanford()
    x2s.stanfordize_file(xl_in, xl_out)


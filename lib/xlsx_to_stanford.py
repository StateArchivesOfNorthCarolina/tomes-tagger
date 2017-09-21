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
        while "  " in pattern:
            pattern = pattern.replace("  ", " ")
 
        # ???
        prefix = "(?i)"
        if is_case_sensitive:
            prefix = ""
        
        # ???
        regx_map = {"{abc}":".*[a-zA-Z]", "{123}":".*[0-9]", "{abc123}":".*[a-zA-Z0-9]"}
        retoken = lambda t: prefix + t if t not in regx_map.keys() else regx_map[t]
        pattern = [retoken(t) for t in pattern.split()]
        pattern = " ".join(pattern)

        # ???
        #if not is_case_sensitive:
        #    for regx_key in regx_map.keys():
        #        if prefix + regx_key in pattern:
        #            self.logger.warning("Illegal wildcard. Wilcards must be standalone tokens.")

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


    def _get_tsv_file(self, xlsx_file, tsv_file):
        """ ??? """
        
        # ???
        if tsv_file is None:
            tsv_file = xlsx_file.replace(".xlsx", "__mapping.txt")
        if os.path.isfile(tsv_file):
            self.logger.warning("File '{}' already exists and will be overwritten.".format(
                tsv_file))

        return tsv_file

        
    def _get_entity_rows(self, xlsx_file):
        """ ??? """

        # load workbook; verify that required worksheet exists.
        workbook = load_workbook(xlsx_file, read_only=False, data_only=True)
        try:
            entity_rows = workbook[self.entity_worksheet]
        except KeyError:
            self.logger.error("Missing required worksheet '{}' in workbook: {}".format(
                    self.entity_worksheet, xlsx_file))
            raise

        return entity_rows


    def stanfordize_file(self, xlsx_file, tsv_file=None):
        """ ??? """
            
        # ???
        self.logger.info("Loading workbook: {}".format(xlsx_file))
        entity_rows = self._get_entity_rows(xlsx_file)
        tsv_file = self._get_tsv_file(xlsx_file, tsv_file)

        # ???
        tsv = open(tsv_file, "w")
        tsv_writer = csv.writer(tsv, delimiter="\t", lineterminator="")
        
        #
        i = 1
        for row in entity_rows.values:

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
            if i != 1 and i != entity_rows.max_row:
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
    xl_out = None#xl_in.replace(".xlsx", "_stanford.txt")

    x2s = XLSXToStanford()
    x2s.stanfordize_file(xl_in, xl_out)


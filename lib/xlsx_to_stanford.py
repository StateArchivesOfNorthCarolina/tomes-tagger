#!/usr/bin/env python3

"""
This module ... ???

Todo:
    * Do you need to handle/skip blank rows?
    * Have the regexmap be a default param in __init__.
"""

# import modules.
import csv
import logging
import os
from openpyxl import load_workbook


class XLSXToStanford():
    """ A class for ... ??? """


    def __init__(self, required_worksheet="Entities", required_headers=("pattern", 
        "description", "case_sensitive", "label", "authority"), charset="utf-8"):
        """ Sets instance attributes. """
        
        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # ???
        self.required_worksheet = required_worksheet
        self.required_headers = required_headers


    def _interpret_pattern(self, pattern, case_sensitive):
        """ ??? """

        # ???
        if not case_sensitive:
            pattern = "(?i)" + " (?i)".join(pattern.split())

        # ???
        replacements = {"{abc}":".*[a-zA-Z]", "{123}":".*[0-9]", "{abc123}":".*[a-zA-Z0-9]"}
        for match, replacement in replacements.items():
            pattern = pattern.replace("(?i)" + match, match)
            pattern = pattern.replace(match, replacement)

        return pattern


    def stanfordize_file(self, xlsx_file, tsv_file=None):
        """ ??? """
        
        self.logger.info("Loading workbook: '{}'.".format(xlsx_file))
        
        # ???
        workbook = load_workbook(xlsx_file, read_only=False, data_only=True)
        try:
            rows = workbook["Entities"]
        except:
            self.logger.error("Required worksheet '{}' missing.".format(
                self.required_worksheet))
            return
        
        # ???
        i = 1
        with open(tsv_file, "w") as tsv:

            #
            tsv_writer = csv.writer(tsv, delimiter="\t", lineterminator="")
            
            for row in rows.values:

                # validate headers.
                if i == 1:
                    
                    if row != self.required_headers:
                        print(row)
                        self.logger.error("Invalid headers or header order.")
                        return
                        
                # ???
                else:
                    pattern, case_sensitive, label, authority = row[0], row[2], row[3], row[4]
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

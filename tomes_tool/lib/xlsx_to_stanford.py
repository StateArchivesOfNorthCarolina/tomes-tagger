#!/usr/bin/env python3

"""
This module contains a class for converting a TOMES Excel 2007+ (.xlsx) entity dictionary file
to a Python list or a tab-delimited file containing NER mapping rules for Stanford CoreNLP.

Todo:
    * Should you validate the data type for each row, i.e. "_validate_row()"?
        - No: Just trust that data is OK unless we start to see data entry errors. :-]
        - I'm changing my answer to "YES" now!
    * Added logging to get_data and use header validator.
        - Header validator needs to raise an error, NOT the tsv method.
    * Remove "if main: stuff at the end when you are ready.
    * Gotta pre-count rows now that using generator.
    * Gotta handle lists being returned from get_pattern().
    * After you re-write any code, check your examples and docstrings.
"""

# import modules.
import codecs
import hashlib
import logging
import os
from openpyxl import load_workbook


class XLSXToStanford():
    """ A class for converting a TOMES Excel 2007+ (.xlsx) entity dictionary file to a Python
    list or a tab-delimited file containing NER mapping rules for Stanford CoreNLP.
    
    Example:
        >>> x2s = XLSXToStanford()
        >>> #x2s.get_data("entities.xlsx") # returns list version of Excel file.
        >>> x2s.write_stanford("entities.xlsx", "entities.txt") # creates mapping file.
    """


    def __init__(self, entity_worksheet="Entities", charset="utf-8"):
        """ Sets instance attributes.
        
        Args:
            - entity_worksheet (str): The name of the worksheet to read from a given workbook,
            i.e. an Excel file.
            - charset (str): Encoding used when writing to file.
        """
        
        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set attributes.
        self.entity_worksheet = entity_worksheet
        self.charset = charset
        self.required_headers = ("identifier", "pattern", "description", "case_sensitive",
                "label", "authority")


    def _get_hash_prefix(self, xlsx_file):
        """ ??? this will be prepended to @identifier, below, in order to know the version
        of the source Excel file used. (first 6 characters should still be unique enough)
        
        Args:
            - ???
            
        Returns:
            str: ???
        """

        # get checksum of @xlsx_file.
        checksum = hashlib.sha256()
        with open(xlsx_file, "rb") as xf:
            xf_bytes = xf.read()
        checksum.update(xf_bytes)

        # truncate checksum.
        hash_prefix = checksum.hexdigest()[:6] + "#"
        
        return hash_prefix 


    def _get_pattern(self, pattern, case_sensitive):
        """ Returns manifestations @pattern without excess whitespace. If @case_sensitive is
        True, also alters @pattern to include case-insensitive regex markup.
        
        Args:
            - pattern (str): The "pattern" field value for a given row.
            - case_sensitive (bool): The "case_sensitive" field value for a given row.

        Returns:
            list: The return value.
            The altered versions of @pattern.
        """

        # remove excess whitespace from @pattern.
        _pattern = " ".join(pattern.strip().split())
        if pattern != _pattern:
            self.logger.warning("Removing excess whitespace in: {}".format(pattern))
            pattern = _pattern
        
        # ???
        is_tomes_pattern = False
        pattern_parts = pattern.split("tomes_pattern:")
        if len(pattern_parts) == 2:
            self.logger.info("???")
            is_tomes_pattern = True
            
        # ???
        if is_tomes_pattern:
            self.logger.info("???")
            try:
                pattern_parts = eval(pattern_parts)
            except SyntaxError as err:
                self.logger.error(err)
                self.logger.warning("??? falling back to ...")
                return []
            try:
                patterns = [i for i in product(*pattern_parts)]
                patterns.reverse()
            except TypeError as err:
                self.logger.error(err)
                self.logger.warning("??? falling back to ...")
                return []

        # if specified, alter @pattern to ignore case provided @is_tomes_pattern is False.
        if not case_sensitive and not is_tomes_pattern:
            tokens = pattern.split(" ")
            pattern = ["(?i)" + token + "(?-i)" for token in tokens]
            pattern = " ".join(pattern)
        elif not case_sensitive and is_tomes_pattern:
            self.logger.warning("??? Ignoring case instruction because ...")
        
        # ???
        if not is_tomes_pattern:
            patterns = [pattern]
            
        return patterns


    def _validate_header(self, header_row):
        """ Determines if @header_row is equal to self.required_headers.
        
        Args:
            - header_row (tuple): The row values for the presumed first row of data.

        Returns:
            bool: The return value.
            True if the header is valid, otherwise False.

        Raises:
            - ??? ... if invalid.
        """
        
        self.logger.info("Validating header row: {}".format(header_row))
        
        # if header is value, return True.
        if header_row == self.required_headers:
            self.logger.info("Header row is valid.")
            return True
        
        # otherwise, report on errors and return False.
        
        # find missing header fields.
        missing_headers = [header for header in self.required_headers if header not in
                header_row]
        if len(missing_headers) != 0:
            self.logger.warning("Missing headers: {}".format(missing_headers))

        # find extra header fields.
        extra_headers = [header for header in header_row if header not in 
                self.required_headers]
        if len(extra_headers) != 0:
            self.logger.warning("Found extra headers: {}".format(extra_headers))
  
        return False

        
    def _get_rows(self, xlsx_file):
        """ Gets iterable version of row data for worksheet (self.entity_worksheet) for a 
        given workbook (@xlsx_file).
        
        Args:
            - xlsx_file (str): The path to the Excel file to load.

        Returns:
            openpyxl.worksheet.worksheet.Worksheet: The return value.
            ??? It's a genererator now.

        Raises:
            - ???
        """

        # load workbook.
        workbook = load_workbook(xlsx_file, read_only=False, data_only=True)
        
        # verify that required worksheet exists.
        try:
            entity_rows = workbook[self.entity_worksheet].iter_rows()
        except KeyError as err:
            self.logger.error(err)
            self.logger.warning("Missing required worksheet '{}' in workbook: {}".format(
                    self.entity_worksheet, xlsx_file))
            raise err

        return entity_rows


    def get_data_dict(self, xlsx_file):
        """ ???

        Args:
            - ???
        
        Returns:
            list: ???
            
        """

        # load workbook; get row data and modified checksum.
        self.logger.info("Loading workbook: {}".format(xlsx_file))
        entity_rows = self._get_rows(xlsx_file)
        hash_prefix = self._get_hash_prefix(xlsx_file)

        # get header.
        row = next(entity_rows)
        header = [cell.value for cell in row]
        
        # ???
        for row in entity_rows:
            row_tuple = [(header[i], row[i].value) for i in range(0,len(header))]
            row_dict = dict(row_tuple)
            row_dict["identifier"] = hash_prefix + row_dict["identifier"]
            yield(row_dict)

        return


    def write_stanford(self, xlsx_file, stanford_file):
        """ Converts @xlsx_file to a CoreNLP mapping file (@stanford_file).
        
        Args:
            - xlsx_file (str): The path to the Excel file to convert.
            - stanford_file (str): The output path for the converted file.

        Returns:
            None

        Raises:
            FileExistsError: If @stanford_file already exists.
        """
        
        # raise error if @stanford_file already exists.
        if os.path.isfile(stanford_file):
            err = "Destination file '{}' already exists.".format(stanford_file)
            self.logger.error(err)
            raise FileExistsError(err)

        # load workbook; get row data and modified checksum.
        self.logger.info("Loading workbook: {}".format(xlsx_file))
        entity_rows = self.get_data_dict(xlsx_file)
        hash_prefix = self._get_hash_prefix(xlsx_file)
       
        # open @stanford_file for writing.
        tsv = codecs.open(stanford_file, "w", encoding=self.charset)

        # iterate through rows; write data to @stanford_file.
        #???self.logger.info("Writing to mapping file: {}".format(stanford_file))
        i = 0
        total_rows = sum(1 for d in self.get_data_dict(xlsx_file))
        for row in entity_rows:
            
            # get cell data.
            identifier = row["identifier"]
            pattern = self._get_pattern(row["pattern"], row["case_sensitive"])[0]
            label = "::".join([identifier, row["authority"], row["label"]])

            # write row to file and avoid final linebreak (otherwise CoreNLP will crash).
            tsv.write("\t".join([pattern,label]))
            if i != total_rows - 1:
                tsv.write("\n")
            i += 1

        return


if __name__ == "__main__":
    #pass
    x2s = XLSXToStanford()
    x2s.write_stanford("../../NLP/TOMES_Entity_Dictionary.xlsx", "mapping.txt")
    d = x2s.get_data_dict("../../NLP/TOMES_Entity_Dictionary.xlsx")

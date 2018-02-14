#!/usr/bin/env python3

""" This module contain a class for converting a TOMES Excel 2007+ (.xlsx) entity dictionary
file to Stanford CoreNLP compliant text files or JSON files. """

# import modules.
import sys; sys.path.append("..")
import codecs
import json
import logging
import logging.config
import os
import plac
import sys
import yaml
from tomes_tool.lib.xlsx_to_entities import XLSXToEntities


class Entities():
    """ A class for converting a TOMES Excel 2007+ (.xlsx) entity dictionary file to Stanford
    CoreNLP compliant text files or JSON files.
    
    Example:
    >>> entities = Entities("../NLP/foo.xlsx")
    >>> #entities.entities() # generator.
    >>> entities.write_json("mappings.json")
    >>> entities.write_stanford("mappings.txt")
    """


    def __init__(self, xlsx_file, is_main=False):
        """ Sets instance attributes.

        Args:
            - xlsx_file (str): The path to the Excel containing a valid TOMES "Entities" 
            worksheet.
            - is_main (bool): Use True if using command line access to this script, i.e. 
            main().
        """

        # set logging.
        self.logger = logging.getLogger(__name__)        
        self.logger.addHandler(logging.NullHandler())
        
        # set attributes.
        self.xlsx_file = xlsx_file
        self.is_main = is_main
        
        # compose instances.
        self.x2e = XLSXToEntities()


    def _check_output(self, output_file):
        """ Checks if @output_file already exists.

        Args:
            - output_file (str): The file to be written.

        Returns
            None
        
        Raises:
            FileExistsError: If @output_file already exists and if @self.is_main is False. 
            Otherwise it will call sys.exit().
        """

        # check if @output_file already exists.
        if os.path.isfile(output_file):
            err = "Destination file '{}' already exists.".format(output_file)
            self.logger.error(err)
            if self.is_main:
                self.logger.info("Exiting.")
                sys.exit(1)
            else:
                raise FileExistsError(err)

        return
            
    
    def entities(self):
        """ Returns a generator containing a mapped entity row (dict) for each row in 
        @self.xlsx_file.
        
        Returns:
            generator: The return value.
            Note: A invalid header will result in an empty generator.

        Raises:
            - FileNotFoundError: If @self.xlsx_file doesn't exist and if @self.is_main is
            False. Otherwise it will call sys.exit().
            - KeyError: If the required "Entities" worksheet can't be retrieved and if
            @self.is_main is False. Otherwise it will call sys.exit().
            - self.x2e.SchemaError: If the worksheet header is invalid and if @self.is_main 
            is False. Otherwise it will call sys.exit().
        """

        # ensure @self.xlsx_file exists.
        if not os.path.isfile(self.xlsx_file):
            msg = "Can't find file: {}".format(self.xlsx_file)
            if self.is_main:
                self.logger.error(msg)
                self.logger.info("Exiting.")
                sys.exit(1)
            else:
                raise FileNotFoundError(msg)
        
        # get entities from @self.xlsx_file.
        self.logger.info("Getting data from: {}".format(self.xlsx_file))
        try:
            entities = self.x2e.get_entities(self.xlsx_file)
        except (KeyError, self.x2e.SchemaError) as err:
            self.logger.error(err)
            if self.is_main:
                self.logger.info("Exiting.")
                sys.exit(1)
            else:
                raise err

        return entities


    def write_stanford(self, stanford_file):
        """ Converts @self.xlsx_file to a CoreNLP mapping file (@stanford_file).
        
        Args:
            - stanford_file (str): The output path for the converted file.

        Returns:
            None
        """

        # ensure @stanford_file doesn't already exist.
        self._check_output(stanford_file)

        # get entities.
        entities = self.entities()

        # open @stanford_file for writing.
        self.logger.info("Writing Stanford file: {}".format(stanford_file))
        tsv = codecs.open(stanford_file, "w", encoding="utf-8")

        # iterate through rows; write data to @stanford_file.
        linebreak = False
        for entity in entities:

            # get cell data.
            tag = entity["identifier"], entity["authority"], entity["label"]
            tag = "::".join(tag)
            manifestations = entity["manifestations"]

            # write row to file and avoid final linebreak (otherwise CoreNLP will crash).
            for manifestation in manifestations:
                if linebreak:
                    tsv.write("\n")
                else:
                    linebreak = True
                tsv.write("\t".join([manifestation,tag]))

        tsv.close()
        return


    def write_json(self, json_file):
        """ Converts @self.xlsx_file to a JSON file (@json_file).
        
        Args:
            - json_file (str): The output path for the converted file.

        Returns:
            None
        """

        # ensure @json_file doesn't already exist.
        self._check_output(json_file)

        # get entities.
        entities = self.entities()

        # open @json_file for writing.
        self.logger.info("Writing JSON file: {}".format(json_file))
        jsv = codecs.open(json_file, "w", encoding="utf-8")
        jsv.write("[")

        # iterate through rows; write data to @json_file.
        bracket = True
        for entity in entities:
            if bracket:
                bracket = False
            else:
                jsv.write(",\n")
            jsv.write(json.dumps(entity, indent=2))
        jsv.write("]")

        jsv.close()
        return


# CLI.
def main(xlsx: "Excel 2007+ entity dictionary file", 
        output: ("file destination (use '.json' extension for JSON output)")):

    "Converts TOMES Entity Dictionary to Stanford file or JSON file.\
    \nexample: `py -3 entities.py ../tests/sample_files/sampleEntities.xlsx` mappings.txt"

    # make sure logging directory exists.
    logdir = "log"
    if not os.path.isdir(logdir):
        os.mkdir(logdir)

    # get absolute path to logging config file.
    config_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(config_dir, "logger.yaml")
    
    # load logging config file.
    with open(config_file) as cf:
        config = yaml.safe_load(cf.read())
    logging.config.dictConfig(config)
    
    # if @output ends in ".json" write JSON file; otherwise write Stanford file.
    entities = Entities(xlsx, is_main=True)
    if output[-5:] == ".json":
        entities.write_json(output)
    else:
        entities.write_stanford(output)
        

if __name__ == "__main__":
    
    import plac
    plac.call(main)
    

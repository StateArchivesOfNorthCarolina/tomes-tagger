#!/usr/bin/env python3

""" This module contain a class for converting a TOMES Excel 2007+ (.xlsx) entity dictionary
file to Stanford CoreNLP compliant text files or JSON files. """

# import modules.
import sys; sys.path.append("..")
import json
import logging
import logging.config
import os
import plac
import yaml
from tomes_tool.lib.xlsx_to_entities import XLSXToEntities


class Entities():
    """ A class for converting a TOMES Excel 2007+ (.xlsx) entity dictionary file to Stanford
    CoreNLP compliant text files or JSON files.
    
    Example:
    >>> entities = Entities("../tests/sample_files/sampleEntityDictionary.xlsx")
    >>> #entities.entities() # generator.
    >>> entities.write_json("mappings.json")
    >>> entities.write_stanford("mappings.txt")
    """


    def __init__(self, xlsx_file):
        """ Sets instance attributes.

        Args:
            - xlsx_file (str): The path to the Excel containing a valid TOMES "Entities" 
            worksheet.
        """

        # set logging.
        self.logger = logging.getLogger(__name__)        
        self.logger.addHandler(logging.NullHandler())
        
        # set attributes.
        self.xlsx_file = xlsx_file
        
        # compose instances.
        self.x2e = XLSXToEntities()
            
    
    def entities(self):
        """ Returns a generator containing a mapped entity row (dict) for each row in 
        @self.xlsx_file.
        
        Returns:
            generator: The return value.

        Raises:
            - FileNotFoundError: If @self.xlsx_file doesn't exist.
            - KeyError: If the required "Entities" worksheet can't be retrieved.
            - self.x2e.SchemaError: If the worksheet header is invalid.
        """

        # ensure @self.xlsx_file exists.
        if not os.path.isfile(self.xlsx_file):
            msg = "Can't find file: {}".format(self.xlsx_file)
            raise FileNotFoundError(msg)
        
        # get entities from @self.xlsx_file.
        self.logger.info("Getting data from: {}".format(self.xlsx_file))
        try:
            entities = self.x2e.get_entities(self.xlsx_file)
        except (KeyError, self.x2e.SchemaError) as err:
            self.logger.error(err)
            raise err

        return entities


    def write_stanford(self, output_file):
        """ Converts @self.xlsx_file to a CoreNLP mapping file.
        
        Args:
            - output_file (str): The output path for the converted file.

        Returns:
            None

        Raises:
            FileExistsError: If @output_file already exists.
        """

        # ensure @output_file doesn't already exist.
        if os.path.isfile(output_file):
            err = "Destination file '{}' already exists.".format(output_file)
            self.logger.error(err)
            raise FileExistsError(err)

        # get entities.
        entities = self.entities()

        # open @output_file for writing.
        self.logger.info("Writing Stanford file: {}".format(output_file))
        tsv = open(output_file, "w", encoding="utf-8")

        # iterate through rows; write data to @output_file.
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


    def write_json(self, output_file):
        """ Converts @self.xlsx_file to a JSON file.
        
        Args:
            - output_file (str): The output path for the converted file.

        Returns:
            None

        Raises:
            FileExistsError: If @output_file already exists.
        """

        # ensure @output_file doesn't already exist.
        if os.path.isfile(output_file):
            err = "Destination file '{}' already exists.".format(output_file)
            self.logger.error(err)
            raise FileExistsError(err)

        # get entities.
        entities = self.entities()

        # open @output_file for writing.
        self.logger.info("Writing JSON file: {}".format(output_file))
        jsv = open(output_file, "w", encoding="utf-8")
        jsv.write("[")

        # iterate through rows; write data to @output_file.
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
def main(xlsx: ".xlsx entity dictionary file", 
        output: ("file destination (use '.json' extension for JSON)"),
        silent: ("disable console logs", "flag", "s")):

    "Converts TOMES Entity Dictionary to Stanford file or JSON file.\
    \nexample: `py -3 entities.py ../tests/sample_files/sampleEntityDictionary.xlsx mappings.txt`"

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
    if silent:
        config["handlers"]["console"]["level"] = 100
    logging.config.dictConfig(config)
    
    # create class instance.
    entities = Entities(xlsx)
    
    # set write method depending on extension of @output.
    write_func = entities.write_stanford
    if output[-5:] == ".json":
        write_func = entities.write_json
    
    # write @output.
    logging.info("Running CLI: " + " ".join(sys.argv))
    try:
        write_func(output)
        logging.info("Done.")
        sys.exit()
    except Exception as err:
        sys.exit(err)
        

if __name__ == "__main__":
    
    import plac
    plac.call(main)
    

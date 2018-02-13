#!/usr/bin/env python3

""" This module contain a class for converting a TOMES Excel 2007+ (.xlsx) entity dictionary
file to Stanford CoreNLP compliant text files or JSON files containing all the row data.

Todo:
    * If xlsx_file doesn't exist, you need to raise an error.
    * Prevent files from beign written if no entities are found (len < 2). Otherwise, you 
    get an end bracket with JSON. :-)
"""

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
    CoreNLP compliant text files or JSON files containing all the row data.
    
    Example:
    >>> entities = Entities("../NLP/foo.xlsx")
    >>> entities.entities() # generator.
    >>> entities.write_json("mappings.json")
    >>> entities.write_stanford("mappings.txt")
    """


    def __init__(self, xlsx_file, is_main=False):
        """ Sets instance attributes.

        Args:
            - xlsx_file (str): The path to the Excel containing a valid TOMES "Entities" 
            worksheet.
            - is_main (bool): Use True if using command line access to this script, i.e. 
            main()
        """

        # set logging.
        self.logger = logging.getLogger(__name__)        
        self.logger.addHandler(logging.NullHandler())
        
        # set attributes.
        self.xlsx_file = xlsx_file
        self.is_main = is_main
        
        # compose instances.
        self.x2e = XLSXToEntities()

    
    def entities(self):
        """ Returns a generator containing a mapped entity row (dict) for each row in 
        @self.xlsx_file.
        
        Returns:
            generator: The return value.
            Note: A invalid header will result in an empty generator.

        Raises:
            - KeyError: If the required "Entities" worksheet can't retrieved and if 
            self.is_main is False. Otherwise it will call sys.exit().
        """

        self.logger.info("Getting data from: {}".format(self.xlsx_file))
        try:
            entities = self.x2e.get_entities(self.xlsx_file)
        except KeyError as err:
            self.logger.error(err)
            if self.is_main:
                self.logger.info("Exiting.")
                sys.exit(1)
            else:
                raise KeyError(err)

        return entities


    def write_stanford(self, stanford_file):
        """ Converts @self.xlsx_file to a CoreNLP mapping file (@stanford_file).
        
        Args:
            - stanford_file (str): The output path for the converted file.

        Returns:
            None

        Raises:
            FileExistsError: If @stanford_file already exists and if self.is_main is False. 
            Otherwise it will call sys.exit().
        """

        # check if @stanford_file already exists.
        if os.path.isfile(stanford_file):
            err = "Destination file '{}' already exists.".format(stanford_file)
            self.logger.error(err)
            if self.is_main:
                self.logger.info("Exiting.")
                sys.exit(1)
            else:
                raise FileExistsError(err)

        # open @stanford_file for writing.
        self.logger.info("Writing Stanford file: {}".format(stanford_file))
        tsv = codecs.open(stanford_file, "w", encoding="utf-8")
        
        # iterate through rows; write data to @stanford_file.
        linebreak = False
        for entity in self.entities():
            
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


    def write_json(self, json_file, charset="utf-8"):
        """ Converts @self.xlsx_file to a JSON file (@json_file).
        
        Args:
            - json_file (str): The output path for the converted file.
            - charset (str): The encoding with which to write @json_file.
                
        Returns:
            None
            
        Raises:
            FileExistsError: If @json_file already exists and if self.is_main is False. 
            Otherwise it will call sys.exit().
        """

        # check if @json_file already exists.
        if os.path.isfile(json_file):
            err = "Destination file '{}' already exists.".format(json_file)
            self.logger.error(err)
            if self.is_main:
                self.logger.info("Exiting.")
                sys.exit(1)
            else:
                raise FileExistsError(err)

        # write @json_file.
        self.logger.info("Writing JSON file: {}".format(json_file))
        bracket = True
        with codecs.open(json_file, "w", encoding=charset) as jf:

            for entity in self.entities():
                if bracket:
                    jf.write("[")
                    bracket = False
                else:
                    jf.write(",\n")
                jf.write(json.dumps(entity, indent=2))
            jf.write("]")

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
    config_file = os.path.join(config_dir, "entities_logger.yaml")
    
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
    

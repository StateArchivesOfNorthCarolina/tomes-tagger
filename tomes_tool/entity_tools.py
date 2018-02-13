#!/usr/bin/env python3

""" This module ... 

Todo:
    * Clean up.
    * Add CLI options.
"""

# import modules.
import sys; sys.path.append("..")
import codecs
import json
import logging
import logging.config
import os
import plac
import yaml
from tomes_tool.lib.xlsx_to_stanford import XLSXToStanford


class EntityTools():
    """ ??? """


    def __init__(self, xlsx_file):
        """ Sets instance attributes.

        ???
        """

        # ???
        self.xlsx_file = xlsx_file
        self.x2s = XLSXToStanford()

    
    def entities(self):
        """ ??? """

        try:
            entities = self.x2s.get_entities(self.xlsx_file)
        except Exception as err:
            pass
            # ???

        return entities


    def write_stanford(self, stanford_file):
        """ ??? """

        try:
            self.x2s.write_stanford(self.xlsx_file, stanford_file)
        except Exception as err:
            pass
            # ???
        return


    def write_json(self, json_file, charset="utf-8"):
        """ ??? """

        # ???
        if os.path.isfile(json_file):
            raise FileExistsError

        # ???
        i = 0
        with codecs.open(json_file, "w", encoding=charset) as jf:
            jf.write("[")

            for entity in self.entities():
                entity = json.dumps(entity, indent=2)
                if i != 0:
                    jf.write(",\n")
                jf.write(entity)
                i += 1
            jf.write("]")

        return


if __name__ == "__main__":
    #pass
    import logging
    logging.basicConfig(level="DEBUG")
    ets = EntityTools("../NLP/foo.xlsx")
    for e in ets.entities():
        print(e)
    ets.write_json("foo.json")
    ets.write_stanford("foo.tsv")

    

#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import json
import logging
import unittest
import random
from tomes_tool.lib.xlsx_to_entities import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_XLSXToEntities(unittest.TestCase):


    def setUp(self):
        
        # set attributes.
        self.x2e = XLSXToEntities()
        self.sample_file = "sample_files/sampleEntityDictionary.xlsx"


    def test__count_entities(self):
        
        # ???
        manifestations_count = 0
        entities = self.x2e.get_entities(self.sample_file)
        for entity in entities:
            manifestations = entity["manifestations"]
            manifestations_count += len(manifestations)

        self.assertTrue(manifestations_count == 10)


# CLI TEST.
def main():
    
    ".\
    \nexample: `py -3 test__xlsx_to_entities"

    # ???
    x2e = XLSXToEntities()


if __name__ == "__main__":
    
    import plac
    plac.call(main)


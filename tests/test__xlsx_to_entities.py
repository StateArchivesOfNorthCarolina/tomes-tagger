#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import logging
import unittest
from tomes_tool.lib.xlsx_to_entities import *

# enable logging.
logging.basicConfig(level=logging.WARNING)


class Test_XLSXToEntities(unittest.TestCase):


    def setUp(self):
        
        # set attributes.
        self.x2e = XLSXToEntities()
        self.sample_file = "sample_files/sampleEntityDictionary.xlsx"


    def test__count_entities(self):
        """ Is the number of pattern manifestations extracted from @self.sample_file correct?
        """ 
        
        manifestations_count = 0

        # count manifestations.
        entities = self.x2e.get_entities(self.sample_file)
        for entity in entities:
            manifestations = entity["manifestations"]
            manifestations_count += len(manifestations)

        self.assertTrue(manifestations_count == 10)


# CLI.
def main(pattern: "the pattern to interpret", 
        ignore_case: ("make pattern case-insensitive", "flag", "i")):
    
    "Prints manifestations for a given pattern.\
    \nexample: `py -3 test__xlsx_to_entities \"TOMES_PATTERN: {'A'}, {'-', ' '}, {'B'}\"\
    "

    # get flipped value of flag.
    case = ignore_case != True

    # print pattern.
    x2e = XLSXToEntities()
    results = x2e.get_manifestations(pattern, case, None)
    for result in results:
        print("".join(result))


if __name__ == "__main__":
    
    import plac
    plac.call(main)


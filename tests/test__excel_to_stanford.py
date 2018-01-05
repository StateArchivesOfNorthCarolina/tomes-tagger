#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import json
import logging
import unittest
import random
from lib.excel_to_stanford import *

# enable logging.
logging.basicConfig(level=logging.DEBUG)


class Test_ExcelToStanford(unittest.TestCase):
    """ """

    def setUp(self):
        
        # set attributes.
        pass


# CLI TEST.
def main():
    
    ".\
    \nexample: `py -3 test__excel_to_stanford"

    # ???
    e2s = ExcelToStanfordNLP()


if __name__ == "__main__":
    
    import plac
    plac.call(main)


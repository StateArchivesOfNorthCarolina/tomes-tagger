#!/usr/bin/env python3

""" This script provides a way to test if NER tagging results are as expected. """

# import modules.
import sys; sys.path.append("..")
import codecs
import logging
import os
from glob import glob
from tomes_tool.lib.text_to_nlp import *

# enable logging.
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

# creat tagger instance.
T2N = TextToNLP()


def testDataFile(data_path="ner_tester_data.tsv", results_path="ner_tester_results.tsv"):
    """ Tests NER patterns in @data_file; returns results as a list of tab-delimited data.
    
    Args:
        - data_path (str): The filepath with test data (in the required format).
        - results_path (str): The filepath in which to write the test results.
    
    Returns:
        list: The return value.
    """

    # test if @results_path already exists.
    if os.path.isfile(results_path):
        err = ("'{}' already exists.".format(results_path))
        logger.error(err)
        logger.warning("Delete file '{}' before running '{}'.".format(results_path, 
            __file__))
        raise FileExistsError(err)
    else:
        logger.info("Creating new results file: {}".format(results_path))
        results_file = open(results_path, "w", encoding="utf-8")

    # read @data_path.
    logger.info("Testing data in: {}".format(data_path))    
    with open(data_path) as f:
        test_data = f.read().split("\n")
        
    # write header row.
    header = ["phrase", "returned_phrase", "expected_tag", "tags_found", "score"]
    header = "\t".join(header) + "\n"
    results_file.write(header)

    # get NER tags for each line; write results row.
    line_num = 0
    for line in test_data:
    
        line_num += 1

        # ignore blank lines and comment lines.
        if line == "":
            logger.debug("Skipping blank line at line number: {}".format(line_num))
            continue
        if "#" in line:
            logger.debug("Skipping comment line at line number: {}".format(line_num))
            continue

        # split line.
        logger.debug("Testing line number: {}".format(line_num))
        phrase, expected_tag, expectation = line.split("\t")

        # get NER tags; format results.
        ner_tags = T2N.get_NER(phrase)
        returned_phrase, tags_found = "", []
        if len(ner_tags) != 0:
            returned_phrase += "".join([n[0] + n[2] for n in ner_tags])
            tags_found = set([n[1] for n in ner_tags if n[1] != ""])
            tags_found = list(tags_found)

        # determine if the returned tags met the expected output from @data_file.
        if expectation == "TRUE":
            expectation = True
        else:
            expectation = False
        
        # determine how well the test worked; a "1" is perfect.
        score = 0
        if expected_tag in tags_found:
            score = 1/len(tags_found) 

        # write test results row.
        result = [phrase, returned_phrase, expected_tag, tags_found, score]
        result = [str(r) for r in result]
        result = "\t".join(result) + "\n"
        results_file.write(result)
        #break

    # close file.
    results_file.close()
    logger.info("Done.")
    return 
        

### let's test ...
def main():

    results_path = testDataFile()
    logging.info("Created results file: {}".format(results_path))

if __name__ == "__main__":
    main()


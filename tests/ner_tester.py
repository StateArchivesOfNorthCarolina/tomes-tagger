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


def testDataFile(data_path="ner_tester_data.tsv", results_path="ner_tester_results.tsv"):
    """ Tests NER patterns in @data_path and writes results to @results_path.
    
    Args:
        - data_path (str): The filepath with test data (in the required format).
        - results_path (str): The filepath in which to write the test results.
    
    Returns:
        None

    Raises:
        FileExistsError: If @results_path already exists.
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
    
    # creat tagger instance.
    t2n = TextToNLP()

    # write header row.
    header = ["phrase", "returned_phrase", "expected_tag", "tags_found", "is_match_expected",
            "is_as_expected", "exactness_score"]
    header = "\t".join(header) + "\n"
    results_file.write(header)

    # get NER tags for each line in @data_path; write results row.
    line_num = 0
    tested_lines = 0
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
        logger.debug("Testing line: {}".format(line_num))
        try:
            phrase, expected_tag, is_match_expected = line.split("\t")
            tested_lines += 1
        except ValueError as err:
            logger.error(err)
            logger.error("Found {} tabs; expected 3.".format(line.count("\t")))
            logger.warning("Skipping invalid line: {}".format(line_num))
            continue
        
        # determine if @expected_tag SHOULD be returned via tagging.
        if is_match_expected == "TRUE":
            is_match_expected = True
        else:
            is_match_expected = False

        # get NER tags; format results.
        ner_tags = t2n.get_NER(phrase)
        tokens_found, tags_found = [], []
        if len(ner_tags) != 0:
            tokens_found = [n[0] for n in ner_tags]
            tags_found = [n[1] for n in ner_tags]

        # determine if matching went as expected. 
        if is_match_expected and expected_tag == tags_found[0]:
            is_as_expected = True
        elif not is_match_expected and expected_tag != tags_found[0]:
            is_as_expected = True
        else:
            is_as_expected = False

        # determine how exactly the tag results matched the @expected_tag.
        # "1" means only the @expected_tag was found while anything else greater than "0"
        # likely means that the @phrase was tokenized and the matching tag applies to only 
        # part of the @phrase.
        exactness_score = 0
        if expected_tag in tags_found:
            exactness_score = 1/len(tags_found)
        
        # write test results row.
        result = [phrase, tokens_found, expected_tag, tags_found, is_match_expected, 
                is_as_expected, exactness_score]
        result = [str(r) for r in result]
        result = "\t".join(result) + "\n"
        results_file.write(result)

    # close file.
    results_file.close()
    logger.info("Tested {} lines out of {}.".format(tested_lines, line_num))
    return 
        

# CLI.
def main(test_data:"path to tab-delimited test data", 
        report_file:"destination file for test results"):
    
    "Creates tab-delimited report file for NER tagging of test data.\
    \nexample: `py -3 ner_tester.py test_data.tsv report_file.tsv`"

    results_path = testDataFile(test_data, report_file)
    logging.info("Created results file: {}".format(results_path))

if __name__ == "__main__":
    
    import plac
    plac.call(main)


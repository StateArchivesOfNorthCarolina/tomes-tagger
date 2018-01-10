#!/usr/bin/env python3

"""
todo:
    * You really need to move this in "tests" and call the new CoreNLP wrapper.
        - Otherwise, you'll have to redo all our default options.
        - This shouldn't be a unit test though.
    * You need to output to UTF-8 file only (no screen).
    * You need to add ratios and the "expected" to the TSV.
"""

# import modules.
import codecs
import os
from glob import glob
from pycorenlp import StanfordCoreNLP

# set CoreNLP port.
# note: CoreNLP server must be running a la: 
# "$ java -mx2g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000".
NLP = StanfordCoreNLP("http://localhost:9003")

def testNER(phrase, label):
    """ Gets NER tags for given @phrase and report if it matches the expected NER tag @label.
    
    Args:
        phrase (str): The text from which to extract NER.
        label (str): The label for the NER tag pattern ("PII.beacon_id", etc.).
    
    Returns:
        tuple: 
            - rephrase (str): the re-joined tokenization of @phrase.
            - ner_tags (list): the list of NER tags found.

    Examples:
        >>> testNER("foo@bar.com", "PII.email_address")
        ('foo@bar.com', ['PII.email_address'])
    """

    # set RegexNER mapping file.
    mapping = "regexner_TOMES/mappings.txt"

    #set RegexNER default tags to always replace on match.
    background_symbol = ["DATE", "DURATION", "LOCATION", "MISC", "MONEY", "NUMBER", "O",
             "ORDINAL", "ORGANIZATION", "PERCENT", "PERSON", "SET", "TIME"]
    background_symbol = ",".join(background_symbol)
    
    # run CoreNLP on @phrase with @mapping file.
    properties = {"annotators":"tokenize, ssplit, pos, ner, regexner",
                 "outputFormat":"json",
                 "regexner.backgroundSymbol": background_symbol,
                 "regexner.mapping":mapping}
    output = NLP.annotate(phrase, properties=properties)
    #print(output)
    
    # get tokens from output.
    tokens = output["sentences"][0]["tokens"]
    
    # get words from @tokens; re-join into single string.
    word = [t["word"] for t in tokens]
    rephrase = " ".join(word)
    
    # get non-empty NER tags.
    ner = [t["ner"] for t in tokens]
    ner_tags = [n for n in ner if n != "O"]
    ner_tags = list(set(ner_tags))

    return (rephrase, ner_tags)


def testDataFile(data_file="ner_test_data.txt"):
    """ Tests NER patterns in @data_file; returns results as a list of tab-delimited data.
    
    Args:
        - data_file (str): The filepath with test data in the required format.
    
    Returns:
        list: The return value.
    """
    
    # create empty output list.
    tsv = []

    # append @tsv header.
    header = ["phrase", "returned_phrase", "expected_tag", "tags_found", "is_passed"]
    header = "\t".join(header)
    tsv.append(header)

    # read test @data_file.
    with open(data_file) as f:
        test_data = f.read().split("\n")


    # runs tests; determine if each test passed or not; append results to @tsv.
    for line in test_data:

        if line == "":
            continue

        phrase, label, expected = line.split("\t")
        rephrase, ner_tags = testNER(phrase, label)

        # ???
        if expected == "TRUE":
            expected = True
        else:
            expected = False

        # ???
        if len(ner_tags) == 0:
            ner_tags = [""]
        
        # determine if a match is successful (True) or not (False).
        if expected and label == ner_tags[0]:
            passed = True
        elif not expected and label != ner_tags[0]:
            passed = True
        else:
            passed = False
        
        # append test data to @tsv.
        test = [phrase, rephrase, label, ner_tags, passed]
        test = [str(r) for r in test]
        test = "\t".join(test)
        tsv.append(test)
        #break

    # convert list to tsv data.
    tsv = "\n".join(tsv)
    return tsv
        

### let's test ...
def main():
    results = testDataFile()
    print(results)

if __name__ == "__main__":
    main()

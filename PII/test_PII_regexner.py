#!/usr/bin/env python3

# import modules.
import codecs
import os
from glob import glob
from pycorenlp import StanfordCoreNLP

# set CoreNLP port.
# note: CoreNLP server must be running a la: 
# "$ java -mx2g -cp "*" edu.stanford.NLP.pipeline.StanfordCoreNLPServer -port 9000".
NLP = StanfordCoreNLP("http://localhost:9000")

def getNER(phrase, PII_type):
    """ Gets NER tags for given @phrase and report if it matches @PII_type.
    
    Args:
        phrase (str): The text to apply NLP to.
        PII_type: The label for the type of PII ("PII.beacon_id", etc.).
    
    Returns:
        tuple: 
            - retext (str): the joined tokens analyzed by CoreNLP (str).
            - ner_tags (list): the list of NER tags found.
            - ner_test (bool): if the only NER tag found equals @PII_type.
            - accuracy (decimal): the ratio of tokens tagged as PII_type divided by the total
              number of tokens analyzed.

    Examples:
        >>> getNER("foo@bar.com", "PII.email_address")
        ('foo@bar.com', ['PII.email_address'], True, 1.0)
    """

    # set RegexNER mapping file.
    mapping = "regexner_TOMES/" + PII_type + "__regexnerMappings.txt"
    
    # run CoreNLP on @phrase with @mapping file.
    properties = {"annotators":"tokenize, ssplit, pos, ner, regexner",
                 "outputFormat":"json",
                 "regexner.mapping":mapping}
    output = NLP.annotate(phrase, properties=properties)
    #print(output)
    
    # get tokens from output.
    tokens = output["sentences"][0]["tokens"]
    
    # get words from @tokens; re-join into single string.
    word = [o["word"] for o in tokens]
    rephrase = " ".join(word)
    
    # get non-empty NER tags; prepare report data.
    ner = [o["ner"] for o in tokens]
    ner_tags = [n for n in ner if n != "O"]
    ner_tags = list(set(ner_tags))
    ner_test = ner_tags == [PII_type] 
    accuracy = len(ner_tags)/len(tokens)
    
    return (rephrase, ner_tags, ner_test, accuracy)


def testPII():
    """ Tests CoreNLP RegexNER PII mappings against test and match data;
        reports resulst as tab-delimied data.
    """
    
    # create empty output list.
    tsv = []

    # append @tsv header.
    header = ["PII_type", "Test_Data", "NER_tags", "isCorrectNER", "NER_Accuracy",
             "isMatchData", "isTestPassed"]
    header = "\t".join(header)
    tsv.append(header)

    # glob all PII folders.
    piis = glob("PII.*/")

    # for each PII type; run getNER() on all test data.
    for pii in piis:
        
        # navigate to PII folder.
        pii = pii[:-1]
        os.chdir(pii)
        
        # open/read test and match data files.
        test_data = open(pii + "__testData.txt")
        match_data = open(pii + "__matchData.txt")
        test_data = test_data.read().split("\n")
        match_data = match_data.read().split("\n")

        # runs tests; determine if each test passed or not; append results to @tsv.
        for line in test_data:
            
            # skip blank lines as they will break getNER().
            if line == "":
                continue

            # run test; determine if test passed.
            phrase, ner_tags, ner_test, accuracy = getNER(line, pii)
            match = phrase in match_data
            if ner_test and match:
                passed = True
            elif ner_test and not match:
                passed = False
            elif not ner_test and match:
                passed = False
            elif not ner_test and not match:
                passed = True
            
            # append test data to @tsv.
            test = [pii, phrase, ner_tags, ner_test, accuracy, match, passed]
            test = [str(r) for r in test]
            test = "\t".join(test)
            tsv.append(test)
        
        # go back up one directory.
        os.chdir("..")
        #break

    # convert list to tsv data.
    tsv = "\n".join(tsv)
    return tsv
        
### let's test ...
SCREEN = False
def main():
    results = testPII()
    if SCREEN == True:
        print(results)
    else:
        with codecs.open("test_PII_regexner.tsv", "w", encoding="utf-8") as f:
            f.write(results)

if __name__ == "__main__":
    main()

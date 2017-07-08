#!/usr/bin/env python3

"""
TODO:
    - The tes should be using the valid() method which I haven't written yet.
        - That's it. Nothing else to test.
"""

# import modules.
import sys; sys.path.append("..")
import hashlib
import os
import tempfile
import unittest
from lib.eaxs_to_tagged import *


class Test_EAXSToTagged(unittest.TestCase):


    def setUp(self):

        self.sample = "sample_files/sampleEAXS.xml"
    
    
    def test__tagging_workflow(self):

        sample = self.sample
        with tempfile.TemporaryFile() as temp:
            tagged_sample = temp.name
        sample_files = [sample, tagged_sample]

        #
        copy = lambda x: x
        
        #
        e2t = EAXSToTagged(copy, copy)
        tagged = e2t.write_tagged(*sample_files)

        #
        hashes = []
        for f in sample_files:
            print(f)
            with open(f, "rb") as f:
                fr = f.read()
                checksum = hashlib.sha256(fr).hexdigest()
                hashes.append(checksum)
        #os.remove(tagged_sample)

        # check if result is expected.
        self.assertEqual(*hashes)
        


# CLI TEST.
def main(eaxs_file: "EAXS file"):

    def mark(s):
        html, nlp = "HTML > NLP", "Text > NLP"
        if s[:len(nlp)] == nlp:
            return html # HTML conversion was run.
        else:
            return nlp # HTML conversion was not run.
    e2t = EAXSToTagged(mark, mark)
    tagged = e2t.write_tagged(eaxs_file, "testTagged.xml")


if __name__ == "__main__":
    import plac
    plac.call(main)


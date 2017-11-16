#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import unittest
from pymets import *


class Test_PyMETS(unittest.TestCase):


    def setUp(self):

        self.pymets = PyMETS()


    def test__validation(self):
        """ Is the sample METS document valid? """

        # test if METS is valid
        sample = make_sample()
        is_valid = self.pymets.validate(sample)

        # check if result is as expected.
        self.assertEqual(True, is_valid)  


def make_sample():
    """ Returns sample METS document as lxml.etree._Element. """

    pymets = PyMETS()

    # create METS root.
    root = pymets.make("mets")
    
    # create <metsHdr>; append to root.
    header = pymets.make("metsHdr")
    root.append(header)
    
    # create header <agent>.
    attributes = {"ROLE":"CREATOR", "TYPE":"OTHER",  "OTHERTYPE":"Software Agent"}
    agent = pymets.make("agent", attributes=attributes)
    header.append(agent)
    name = pymets.make("name")
    name.text = "PyMETS"
    agent.append(name)

    # create <fileSec>.
    fileSec = pymets.make("fileSec")
    fileGrp = pymets.fileGrp(filenames=[__file__], basepath=".", identifier="source_code")
    fileSec.append(fileGrp)
    root.append(fileSec)

    # create <structMap> and <div>.
    structMap = pymets.make("structMap")
    file_ids = pymets.get_fileIDs(fileSec)
    div = pymets.div(file_ids)
    structMap.append(div)
    root.append(structMap)
    
    # add comment.
    root.append(pymets.Comment("This is a comment."))
    
    return root


# CLI TEST.
def main():
    
    "Prints METS file based on current directory."

    stringify = PyMETS.stringify # lxml.etree._Element to string.
    
    # get sample; print to string.
    mets_el = make_sample()
    mets = stringify(self=None, element=mets_el)
    print(mets)


if __name__ == "__main__":

    import plac
    plac.call(main)


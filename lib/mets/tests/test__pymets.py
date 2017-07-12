#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import unittest
from pymets import *


class Test_PyMETS(unittest.TestCase):


    def test__validation(self):
        """ Is it True that ... """

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

        # test if METS is valid
        is_valid = pymets.valid(root)

        # check if result is expected.
        self.assertEqual(True, is_valid)  


if __name__ == "__main__":
    pass


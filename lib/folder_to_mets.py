#!/usr/bin/env python3


"""
TODO:
    - ???
"""

# import modules.
import os
from glob import glob
from mets.pymets import PyMETS


class FolderToMETS():
    """ """

    def __init__(self, path):
        """ """
        
        self.path = path
        self.pymets = PyMETS()
        self.root = self.pymets.make("mets")
        self.build()

    
    def stringify(self):
        """ """

        pymets = self.pymets
        root = self.root
        rootx = pymets.stringify(root)
        return rootx


    def build(self):
       """ """
       
       pymets = self.pymets
       path = self.path
       root = self.root

       # create <metsHdr>.
       header = pymets.make("metsHdr")
       root.append(header)
       
       # create <agent>.
       attributes = {"ROLE":"CREATOR", "TYPE":"OTHER",  "OTHERTYPE":"Software Agent"}
       agent = pymets.make("agent", attributes=attributes)
       name = pymets.make("name")
       name.text = "TOMES Tool"
       agent.append(name)
       header.append(agent)
       
       # create <amdSec>.
       amdSec = pymets.make("amdSec")
       root.append(amdSec)
       techMD = pymets.make("techMD", {"ID":"tmd1"})
       amdSec.append(techMD)
       techmd_01 = pymets.load_template("templates/techmd_01.xml", eaxs_id="test")
       techmd_01 = pymets.wrap(techmd_01, mdtype="PREMIS")
       techMD.append(techmd_01)

       # create <fileSec>.
       fileSec = pymets.make("fileSec")
       root.append(fileSec)

       #
       folders = glob("*/", recursive=True)
       for folder in folders:
           
           #
           fs = glob(folder + "/*.*", recursive=True)
           folder_id = "".join(
                   [c.lower() for c in folder if c.isalnum()]) # alpha-numeric only.
           fileGrp = pymets.fileGrp(filenames=fs, basepath=path, identifier=folder_id)
           fileSec.append(fileGrp)
       
       # create <structMap>.
       structMap = pymets.make("structMap")
       root.append(structMap)
       file_ids = [fid.get("ID") for fid in fileSec.findall("*{*}file")]
       div = pymets.div(file_ids)
       structMap.append(div)

       # append valid() response to root as comment.
       valid = pymets.valid(root)
       valid = "It is {} that this METS document is valid.".format(valid)
       root.append(pymets.Comment(valid))

 


# TEST.
def main():
    f2m = FolderToMETS(".")
    x = f2m.stringify()
    print(x)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3


"""
TODO:
    - You need to fill in the template placeholder variables.
        - Is there a way to generate a list of their names after loading the string?
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

       # load templates.
       templates = glob("templates/*.xml")
       for template in templates:
           t_el = pymets.load_template(template)
           root.append(t_el)
       
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
       file_ids = pymets.get_fileIDs(fileSec)
       div = pymets.div(file_ids)
       structMap.append(div)

       # append valid() response to root as comment.
       valid = pymets.valid(root)
       valid = "It is {} that this METS document is valid.".format(valid)
       root.append(pymets.comment(valid))


# TEST.
def main():
    f2m = FolderToMETS(".")
    x = f2m.stringify()
    print(x)


if __name__ == "__main__":
    main()

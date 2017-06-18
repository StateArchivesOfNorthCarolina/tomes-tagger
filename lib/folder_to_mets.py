#!/usr/bin/env python3

"""
This module contains a class to construct a METS file for a given email account folder with an
EAXS file, an optional attachments folder, an optional tagged EAXS file, and other optional files and folders.

TODO:
    - Need to known naming conventions so this can implicitly figure out the name of the
    tagged EAXS file.
    - Need REAL values for formatting the templates! :-]
    - Make separate fileGrp for attachments? Maybe no: unless you want to break out PREMIS
    more so attachments are a separate object.
    - Make separate fileGrp for tagged EAXS.
    - Make separate fileGrp for all non-required folders (depends on final xIP structure).
    - The template files should be optional (ideally).
"""

# import modules.
import os
from glob import glob
from mets.pymets import PyMETS


class FolderToMETS():
    """ A class to construct a METS file for a given email account folder with an EAXS file,
    an optional attachments folder, an optional tagged EAXS file, and other optional files
    and folders. """


    def __init__(self, path):
        """ Sets instance attributes.
        
        Args:
            - path (str): The path to the account folder containing the EAXS file, etc.
        """
        
        # set attributes.
        self.path = path

        # compose instance of PyMETS; build METS.
        self.pymets = PyMETS()
        self.root = self.pymets.make("mets")
        self.build()


    def stringify(self):
        """ Returns a string representation of the root METS etree element. """

        pymets, root = self.pymets, self.root
        rootx = pymets.stringify(root)
        return rootx


    def build(self):
       """ Builds METS sections, appends sections to root. """
       
       pymets, path, root = self.pymets, self.path, self.root

       # load and format METS templates; append to root.
       subs = {"eaxs_id": "{eaxs_id}", 
               "eaxs_cdate": "{eaxs_cdate}",
               "tagged_eaxs_cdate" : "{tagged_eaxs_cdate}"}
       templates = glob("templates/*.xml")
       for template in templates:
           t_el = pymets.load_template(template, **subs)
           root.append(t_el)
       
       # create <fileSec>.
       fileSec = pymets.make("fileSec")
       root.append(fileSec)

       # make <fileGrp> for each folder.
       folders = glob("*/", recursive=True)
       for folder in folders:
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

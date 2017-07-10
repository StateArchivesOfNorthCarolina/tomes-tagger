#!/usr/bin/env python3

"""
This module contains a class to construct a METS file for a given email account folder with
an EAXS file, an optional attachments folder, an optional tagged EAXS file, and other
optional files and folders.

TODO:
    - Need to known naming conventions so this can implicitly figure out the name of the
    tagged EAXS file.
    - Need REAL values for formatting the templates! :-]
    - Make separate fileGrp for attachments? Maybe no: unless you want to break out PREMIS
    more so attachments are a separate object.
    - Make separate fileGrp for tagged EAXS.
    - Make separate fileGrp for all non-required folders (depends on final xIP structure).
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
        """ Returns a string representation of the root METS etree element.
        
        Returns:
            <class 'str'>
        """

        #
        rootx = self.pymets.stringify(self.root)
        return rootx


    def build(self):
       """ Builds METS sections, appends sections to root. """
       
       # set template substitution strings.
       subs = {"eaxs_id": "{eaxs_id}", 
               "eaxs_cdate": "{eaxs_cdate}",
               "tagged_eaxs_cdate" : "{tagged_eaxs_cdate}",
               "title": "{title}",
               "ctime": "{ctime}",
               "description": "{description}",
               "subject": "{subject}"}

       # load and format METS templates; append to root.
       templates = glob("templates/*.xml")
       for template in templates:
           t_el = self.pymets.load_template(template, **subs)
           self.root.append(t_el)
       
       # create <fileSec>.
       fileSec = self.pymets.make("fileSec")
       self.root.append(fileSec)

       # make <fileGrp> for each folder.
       folders = glob("*/", recursive=True)
       for folder in folders:
           fs = glob(folder + "/*.*", recursive=True)
           folder_id = "".join(
                   [c.lower() for c in folder if c.isalnum()]) # alpha-numeric only.
           fileGrp = self.pymets.fileGrp(filenames=fs, basepath=self.path,
                   identifier=folder_id)
           fileSec.append(fileGrp)
       
       # create <structMap>.
       structMap = self.pymets.make("structMap")
       self.root.append(structMap)
       file_ids = self.pymets.get_fileIDs(fileSec)
       div = self.pymets.div(file_ids)
       structMap.append(div)

       # append valid() response to root as comment.
       valid = self.pymets.valid(self.root)
       valid = "It is {} that this METS document is valid.".format(valid)
       self.root.append(self.pymets.comment(valid))

       return


# TEST.
def main():
    f2m = FolderToMETS(".")
    metsx = f2m.stringify()
    print(metsx)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

"""
This module contains a class to construct a METS file for a given email account folder.

Todo:
    * The templates folder AND the substitution dict need to be passed to the methods rather
    than be assumed.
    * You probably want __init__ to accept args/kwargs then so these can be pass to __init__?
    * This is the only module with side effects. I don't like that. So don't
    declare a self.root in __init__. Have the constructor accept the templates
    as a list of optional files and a "charset". Then explicitly call build()
    to get an etree._Element; stringify() will now take an _Element arg; and
    create a new method to write directly to file. Also, make build() public
    now. You'll need to update the example, too.
"""

# import modules.
import os
from datetime import datetime
from glob import glob
from mets.pymets import PyMETS


class FolderToMETS():
    """ A class to construct a METS file for a given email account folder. 
    
    Example:
        >>> f2m = FolderToMETS("my/EAXS/path/") # specify EAXS folder.
        >>> f2m.root # lxml.etree._Element version of METS.
        >>> f2m.string() # string version of METS.
    """


    def __init__(self, path):
        """ Sets instance attributes.
        
        Args:
            - path (str): The EAXS path.
        """
        
        # set attributes.
        self.path = path

        # compose instance of PyMETS; build METS.
        self.pymets = PyMETS()
        self.root = self.pymets.make("mets")
        self._build()


    def string(self):
        """ Returns a string representation of the root METS etree element.
        
        Returns:
            str: The return value.
        """

        strroot = self.pymets.stringify(self.root)
        return strroot


    def _build(self):
        """ Builds METS document.
        
        Returns:
            None
        """
       
        # set template substitution strings.
        subs = {"eaxs_id": "{eaxs_id}", 
               "eaxs_cdate": "{eaxs_cdate}",
               "tagged_eaxs_cdate" : "{tagged_eaxs_cdate}",
               "mets_ctime": datetime.now().isoformat(),
               "darcmail_version":"darcmail_version",
               "tomes_tool_version":"tomes_tool_version"}

        # load and format METS templates; append to root.
        templates = glob("mets_templates/[!=~]*.[xml|xlsx]")
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

        # append validation response to root as comment.
        is_valid = self.pymets.validate(self.root)
        is_valid = "It is {} that this METS document is valid.".format(is_valid)
        self.root.append(self.pymets.Comment(is_valid))

        return


if __name__ == "__main__":
    
    f2m = FolderToMETS(".")
    print(f2m.string())


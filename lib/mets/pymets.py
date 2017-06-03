#!/usr/bin/env python3

"""
TODO:
    - Add docstrings.
    - Note that struct-links and behavior elements aren't supported.
    - Say this is for METS version 1.11.
    - Put all instantiated mets.* objects in __init__ or a private function.
        - Just need to instantiate once, right?
"""

# import modules.
from lxml import etree
from lib.anyType import AnyType
from lib.div import Div
from lib.fileGrp import FileGrp

# DEPRECATE!
from lib.agent import Agent
from lib.mdSecType import MdSecType
from lib.mdWrap import MdWrap


class PyMETS():
    """ A class with which to create a METS file. """

    
    def __init__(self, prefix="mets", ns={}):
        """ Set instance attributes.

        Args:
            - prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        # set METS namespace prefix. 
        self.prefix = prefix

        # set namespace map using defaults plus user values in @ns.
        self.ns_map = {"mets" : "http://www.loc.gov/METS/",
                      "xlink" : "http://www.w3.org/1999/xlink",
                      **ns}
    
    def make(self, *args, **kwargs):
        """ """

        name_el = AnyType(self.prefix, self.ns_map)
        name_el = name_el.anyType(*args, **kwargs)
        return name_el


    #def agent(self, *args, **kwargs):
    #    """ """

    #    agent_el = self.make("agent", attributes=attributes)
    #    agent_el = 
    #    return agent_el


    def div(self, *args, **kwargs):
        """ """

        div_el = Div(self.prefix, self.ns_map)
        div_el = div_el.div(*args, **kwargs)
        return div_el


    def fileGrp(self, *args, **kwargs):
        """ """

        filegrp_el = FileGrp(self.prefix, self.ns_map)
        filegrp_el = filegrp_el.fileGrp(*args, **kwargs)
        return filegrp_el
    

    #def mdWrap(self, *args, **kwargs):
    #    """ """

    #    mdwrap_el = MdWrap(self.prefix, self.ns_map)
    #    mdwrap_el = mdwrap_el.mdWrap(*args, **kwargs)
    #    return mdwrap_el


# TEST.
def main():
    
    pymets = PyMETS()
    
    # set METS root; append <metsHdr>.
    root = pymets.make("mets")
    header = pymets.make("metsHdr")
    root.append(header)
    
    # append <agent> to header.
    attributes = {"ROLE":"CREATOR", "TYPE":"OTHER",  "OTHERTYPE":"Software Agent"}
    agent = pymets.make("agent", attributes=attributes)
    name = pymets.make("name", text="TOMES Tool")
    note = pymets.make("note", text="TOMES Tool is written in Python.")
    agent.extend([name, note])
    header.append(agent)
    
    # create <dmdSec>; append to root.
    dmdSec = pymets.make("dmdSec", {"ID":"no_metadata"})
    root.append(dmdSec)
    
    # create <fileSec>; append to root.
    fileSec = pymets.make("fileSec")
    fileGrp = pymets.fileGrp(filenames=[__file__], basepath=".", identifier="code")
    fileSec.append(fileGrp)
    root.append(fileSec)

    # get fileSec1 ids; create <structMap>; append to root.
    file_ids = [fid.get("ID") for fid in fileGrp.findall("{*}file")]
    structMap = pymets.make("structMap")
    div = pymets.div(file_ids)
    structMap.append(div)
    root.append(structMap)

    # print METS.
    rootx = etree.tostring(root, pretty_print=True)
    rootx = rootx.decode("utf-8")
    print(rootx)


if __name__ == "__main__":
    main()

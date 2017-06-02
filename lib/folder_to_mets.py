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
from mets.agent import Agent
from mets.div import Div
from mets.fileGrp import FileGrp
from mets.mdSecType import MdSecType
from mets.mdWrap import MdWrap


class FolderToMETS():
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

        # create METS root element.
        self.root = self.make("mets")
        
        # create METS header sub-element.
        self.metsHdr = self.make("metsHdr")
    
    
    def make(self, *args, **kwargs):
        """ """

        name_el = MdSecType(self.prefix, self.ns_map)
        name_el = name_el.mdSecType(*args, **kwargs)
        return name_el


    def agent(self, *args, **kwargs):
        """ """

        agent_el = Agent(self.prefix, self.ns_map)
        agent_el = agent_el.agent(*args, **kwargs)
        return agent_el


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
    

    def mdWrap(self, *args, **kwargs):
        """ """

        mdwrap_el = MdWrap(self.prefix, self.ns_map)
        mdwrap_el = mdwrap_el.mdWrap(*args, **kwargs)
        return mdwrap_el


# TEST.
def main():
    
    f2m = FolderToMETS()
    
    # set METS root; append <metsHdr>.
    root = f2m.root
    header = f2m.metsHdr
    root.append(header)
    
    # append <agent> to header.
    agent1 = f2m.agent("name1", "role1", note="note1")
    agent2 = f2m.agent("name2", "role2")
    header.extend([agent1, agent2])
    
    # create <dmdSec>; append to root.
    dmdSec1 = f2m.make("dmdSec", identifier="dmdSec_1")
    root.append(dmdSec1)
    
    # create <fileSec>; append to root.
    fileSec1 = f2m.make("fileSec")
    fileGrp1 = f2m.fileGrp(["mets/sampleMETS.xml"], ".", "fileGrp_1")
    fileSec1.append(fileGrp1)
    root.append(fileSec1)

    # get fileSec1 ids; create <structMap>; append to root.
    file_ids = [i.get("ID") for i in fileGrp1.findall("{*}file")]
    structMap1 = f2m.make("structMap")
    div1 = f2m.div(file_ids)
    structMap1.append(div1)
    root.append(structMap1)

    # print METS.
    x = etree.tostring(f2m.root, pretty_print=True)
    print(x.decode("utf-8"))


if __name__ == "__main__":
    main()

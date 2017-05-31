#!/usr/bin/env python3

# import modules.
from lxml import etree
from mets.agent import Agent

class FolderToMETS():

    def __init__(self, prefix="mets", ns={}):
        
        self.prefix = prefix
        self.ns_map = {"mets" : "http://www.loc.gov/METS/",
                      "xlink" : "http://www.w3.org/1999/xlink",
                      **ns}
        self.mets = etree.Element("{" + self.ns_map[self.prefix] + "}mets",
                                  nsmap=self.ns_map)
        self.metsHdr = etree.SubElement(self.mets, 
                                      "{" + self.ns_map[self.prefix] + "}metsHdr",
                                      nsmap=self.ns_map)
    
    
    def insert(self, parent, child):
        parent.append(child)
        return

    #def remove(self, parent, child)?

    # should be own class?
    def dmdSec(self, identifier):
        
        dmdsec_el = etree.Element("{" + self.ns_map[self.prefix] + "}dmdSec",
                                   nsmap=self.ns_map)
        dmdsec_el.set("ID", identifier)
        return dmdsec_el


    # should be own class?
    def fileSec(self):
        
        filesec_el = etree.Element("{" + self.ns_map[self.prefix] + "}fileSec",
                                   nsmap=self.ns_map)
        return filesec_el

    
    def agent(self, *args, **kwargs):

        agent_el = Agent(self.prefix, self.ns_map)
        agent_el = agent_el.agent(*args, **kwargs)
        return agent_el


# TEST.
if __name__ == "__main__":
    
    f2m = FolderToMETS()

    root = f2m.mets
    header = f2m.metsHdr
    
    a = f2m.agent("name1", "role1", note="note1")
    b = f2m.agent("name2", "role2")
    f2m.insert(header, a)
    f2m.insert(header, b)
    
    dmd = f2m.dmdSec("id1")
    f2m.insert(root, dmd)
    
    fsc = f2m.fileSec()
    f2m.insert(root, fsc)

    x = etree.tostring(f2m.mets, pretty_print=True)
    print(x.decode("utf-8"))

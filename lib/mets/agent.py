#!/usr/bin/env python3

"""
This module creates a METS <agent> tree for given input. The output can be integrated into a
complete METS file's <metsHdr> element.

TODO:
    - ???
"""

# import modules.
import mets_ns
from lxml import etree


def agent(name, role, note=None, attributes=None):
    """ Creates a METS <agent> etree element.

    Args:
        - name (str): The <name> sub-element's value.
        - role (str): The ROLE attribute value to set for the <agent> element.
        - note (str): Optional <note> sub-element value. 
        - attributes (dict): The optional attributes to set for the <agent>.
    
    Returns:
        <class 'lxml.etree._Element'>
    """
    
    # create <agent> element; set optional attributes and ROLE attribute.
    agent_el = etree.Element(mets_ns.ns_id("mets") + "agent", nsmap=mets_ns.ns_map)
    if attributes is not None:
        for k, v in attributes.items():
            agent_el.set(k, v)
    agent_el.set("ROLE", role)

    # create <name> subelement.
    name_el = etree.SubElement(agent_el, mets_ns.ns_id("mets") + "name", nsmap=mets_ns.ns_map)
    name_el.text = name
    
    # create optional <note> element.
    if note is not None:
        note_el = etree.SubElement(agent_el, mets_ns.ns_id("mets") + "note", nsmap=mets_ns.ns_map)
        note_el.text = note

    return agent_el


# TEST.
def main():

  # set args.
  args = ("TOMES Tool",
          "CREATOR", 
          "TOMES Tool is Python code.",
         {"TYPE":"OTHER", "OTHERTYPE": "Software Agent"})
  agentx = agent(*args)
  return agentx


if __name__ == "__main__":
    
    agentx = main()
    
    # print XML.
    agentx = etree.tostring(agentx, pretty_print=True)
    agentx = agentx.decode("utf-8")
    print(agentx)


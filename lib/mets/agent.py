#!/usr/bin/env python3

# import modules.
from lxml import etree


class Agent():
    """ A class to create a METS <agent> tree for given input. The output can be integrated
    into a complete METS file's <metsHdr> element. """
    
    
    def __init__(self, prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        self.prefix = prefix
        self.ns_map = ns_map 

    
    def agent(self, name, role, note=None, attributes=None):
        """ Creates a METS <agent> etree element.

        Args:
            - name (str): The <name> sub-element's value.
            - role (str): The ROLE attribute value to set for the <agent> element.
            - note (str): Optional <note> sub-element value. 
            - attributes (dict): The optional attributes to set for the <agent>.
        
        Returns:
            <class 'lxml.etree._Element'>
        """
        
        # create <agent> element.
        agent_el = etree.Element("{" + self.ns_map[self.prefix] + "}agent",
                nsmap=self.ns_map)
        
        # set optional attributes and ROLE attribute.
        if attributes is not None:
            for k, v in attributes.items():
                agent_el.set(k, v)
        agent_el.set("ROLE", role)

        # create <name> subelement.
        name_el = etree.SubElement(agent_el,
                "{" + self.ns_map[self.prefix] + "}name",
                nsmap=self.ns_map)
        name_el.text = name
        
        # create optional <note> element.
        if note is not None:
            note_el = etree.SubElement(agent_el,
                    "{" + self.ns_map[self.prefix] + "}note",
                    nsmap=self.ns_map)
            note_el.text = note

        return agent_el


# TEST.
def main():

  from mets_ns import ns_map

  # set args.
  args = ("TOMES Tool",
          "CREATOR", 
          "TOMES Tool is Python code.",
         {"TYPE":"OTHER", "OTHERTYPE": "Software Agent"})
  agent_el = Agent("mets", ns_map)
  agent_el = agent_el.agent(*args)
  return agent_el


if __name__ == "__main__":
    
    agentx = main()

    # print XML.
    agentx = etree.tostring(agentx, pretty_print=True)
    agentx = agentx.decode("utf-8")
    print(agentx)


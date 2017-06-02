#!/usr/bin/env python3

# import modules.
from lxml import etree


class MdSecType():
    """ A class to create a METS ... """
    
    def __init__(self, prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        self.prefix = prefix
        self.ns_map = ns_map 


    def mdSecType(self, name, identifier, attributes=None):
        """ Creates a ...

        Args:
            - name (str): The name of the element to create.
            - identifier (str): The ID attribute value to set for the @name element.
                                Secret: Use "None" to bypass creating this attribute.
            - attributes (dict): The optional attributes to set for the <div>.
        
        Returns:
            <class 'lxml.etree._Element'>
        """
        
        # create @name element.
        name_el = etree.Element("{" + self.ns_map[self.prefix] + "}" + name,
                nsmap=self.ns_map)
        
        # set optional attributes and ID attribute.
        if attributes is not None:
            for k, v in attributes.items():
                name_el.set(k, v)
        if identifier is not None:
            name_el.set("ID", identifier)

        return name_el


# TEST.
def main():

    from mets_ns import ns_map
    
    # create <dmdSec> with some attributes.
    mdsec_el = MdSecType("mets", ns_map)
    mdsec_el = mdsec_el.mdSecType("dmdSec", "dmd1", {"STATUS": "Testing"})
    return mdsec_el


if __name__ == "__main__":
    
    mdsecx = main()
    
    # print XML.
    mdsecx = etree.tostring(mdsecx, pretty_print=True)
    mdsecx = mdsecx.decode("utf-8")
    print(mdsecx)

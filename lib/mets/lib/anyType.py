#!/usr/bin/env python3

# import modules.
from lxml import etree


class AnyType():
    """ A class to create a any METS etree element with optional attributes. """
    

    def __init__(self, ns_prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        self.ns_prefix = ns_prefix
        self.ns_map = ns_map 


    def anyType(self, name, attributes=None):
        """ Creates an element with optional text and attributes.

        Args:
            - name (str): The name of the element to create.
            - attributes (dict): The optional attributes to set.
            
            Each key is the attribute name; each key's value is the attribute value. Inline
            namespace prefixes (ex: "mets:ID") are supported if the prefix is a key in the
            instance's @ns_map. 
        
        Returns:
            <class 'lxml.etree._Element'>
        """
        
        # create @name element.
        name_el = etree.Element("{" + self.ns_map[self.ns_prefix] + "}" + name,
                nsmap=self.ns_map)
        
        # set optional attributes.
        if attributes is not None:
            for attribute, value in attributes.items():
                if ":" in attribute:
                    pref, attr = attribute.split(":") 
                    attribute = "{" + self.ns_map[pref] + "}" + attr
                name_el.set(attribute, value)

        return name_el


if __name__ == "__main__":
    pass


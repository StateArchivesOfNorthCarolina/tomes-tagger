#!/usr/bin/env python3

""" The module contain a class to create any METS element with optional attributes. """

# import modules.
from lxml import etree


class AnyType():
    """ A class to create any METS element with optional attributes. """
    

    def __init__(self, ns_prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - ns_prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        self.ns_prefix = ns_prefix
        self.ns_map = ns_map


    def anyType(self, name, attributes=None):
        """ Creates an element @name with optional attributes.

        Args:
            - name (str): The name of the element to create.
            - attributes (dict): The optional attributes to set. Attribute namespace prefixes
            are supported if the prefix is a key in the instance's @ns_map.
        
        Returns:
            lxml.etree._Element: The return value.
        """
        
        # supported namespace prefixes for elements (e.g. "mets:fileSec").
        if ":" in name:
            pref, name = name.split(":") 
            name_el = "{" + self.ns_map[pref] + "}" + name 
        else:
            pref, name = self.ns_prefix, name
            
        # create @name element.
        name_el = etree.Element("{" + self.ns_map[pref] + "}" + name, nsmap=self.ns_map)
        
        # set optional attributes.
        if attributes is not None:
            
            for attribute, value in attributes.items():
                
                # supported namespace prefixes for attributes (e.g. "mets:ID").
                if ":" in attribute:
                    pref, attr = attribute.split(":") 
                    attribute = "{" + self.ns_map[pref] + "}" + attr
                    
                name_el.set(attribute, value)

        return name_el


if __name__ == "__main__":
    pass


#!/usr/bin/env python3

# import modules.
from lxml import etree


class AnyType():
    """ A class to create a any METS element ... """
    

    def __init__(self, prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        self.prefix = prefix
        self.ns_map = ns_map 


    def anyType(self, name, attributes=None, text=None):
        """ Creates an element using the METS namespace ...

        Args:
            - name (str): The name of the element to create.
            - attributes (dict): The optional attributes to set. Each key is the attribute
                                 name; each key's value is the attribute value.
            - text (str): The optional element text to set.
        
        Returns:
            <class 'lxml.etree._Element'>
        """
        
        # create @name element.
        name_el = etree.Element("{" + self.ns_map[self.prefix] + "}" + name,
                nsmap=self.ns_map)
        
        # set optional attributes.
        if attributes is not None:
            for attribute, value in attributes.items():
                name_el.set(attribute, value)

        # set optional sub-elements.
        if text is not None:
            name_el.text = text

        return name_el


# TEST.
def main():

    from mets_ns import ns_map
    
    # create faek METS element with some attributes and sub-elements.
    attribs = {"baz" : "1", "qux" : "2"}
    anytype = AnyType("mets", ns_map)
    foo = anytype.anyType("foo", attribs)
    bar = anytype.anyType("bar", attribs, "Lorem ipsum.")
    foo.append(bar)
    return foo


if __name__ == "__main__":
    
    anyx = main()
    
    # print XML.
    anyx = etree.tostring(anyx, pretty_print=True)
    anyx = anyx.decode("utf-8")
    print(anyx)

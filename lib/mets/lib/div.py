#!/usr/bin/env python3

# import modules.
from lxml import etree


class Div():
    """ A class to create a METS <div> tree for a given list of files. The output can be
    integrated into a complete METS file's <structMap> element. """
    
    def __init__(self, prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        self.prefix = prefix
        self.ns_map = ns_map 


    def div(self, file_ids, attributes=None):
        """ Creates a METS <div> etree element for each item in @file_ids.

        Args:
            - file_ids (list): The identifiers for each <fptr> element within the <div>.
            - attributes (dict): The optional attributes to set for the <div>.
        
        Returns:
            <class 'lxml.etree._Element'>
        """
        
        # create <div> element.
        div_el = etree.Element("{" + self.ns_map[self.prefix] + "}div",
                nsmap=self.ns_map)
        
        # set optional attributes.
        if attributes is not None:
            for k, v in attributes.items():
                div_el.set(k, v)

        for file_id in file_ids:  

            # create <fptr> element for current file; set FILEID attribute.
            fptr_el = etree.SubElement(div_el, "{" + self.ns_map[self.prefix] + "}fptr",
                    nsmap=self.ns_map)
            fptr_el.set("FILEID", file_id)

        return div_el


# TEST.
def main():

    from mets_ns import ns_map

    # create list of test ids.
    file_ids = ["test_" + str(i) for i in range(0,10)]
    
    # create <div> with some attributes.
    div_el = Div("mets", ns_map)
    div_el = div_el.div(file_ids, {"ID": "ID_div", "LABEL": "Testing"})
    return div_el


if __name__ == "__main__":
    
    divx = main()
    
    # print XML.
    divx = etree.tostring(divx, pretty_print=True)
    divx = divx.decode("utf-8")
    print(divx)

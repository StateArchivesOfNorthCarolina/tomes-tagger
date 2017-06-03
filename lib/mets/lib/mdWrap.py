#!/usr/bin/env python3

# import modules.
from lxml import etree


class MdWrap():
    """ A class to create a METS <mdWrap> tree for given input. The output can be integrated
    into a complete METS file's <dmdSec> element. """


    def __init__(self, prefix, ns_map):
        """ Set instance attributes. 
        
        Args:
            - prefix (str): The METS namespace prefix. 
            - ns_map (dict): Namespace prefixes are keys; namespace URIs are values.
        """
        
        self.prefix = prefix
        self.ns_map = ns_map 


    def mdWrap(self, metadata, mdtype, attributes=None):
        """ Creates a METS <mdWrap> etree element.

        Args:
            - metadata (lxml.etree._Element): The metadata to wrap in the <mdWrap> element.
            - mdtype (str): The MDTYPE attribute value to set for the <mdwrap>.
            - attributes (dict): The optional attributes to set for the <mdWrap>.
        
        Returns:
            <class 'lxml.etree._Element'>
        """
        
        # create <mdWrap> element.
        mdWrap_el = etree.Element("{" + self.ns_map[self.prefix] + "}mdWrap",
                nsmap=self.ns_map)
        
        # set optional attributes and MDTYPE attribute.
        if attributes is not None:
            for k, v in attributes.items():
                mdWrap_el.set(k, v)
        mdWrap_el.set("MDTYPE", mdtype)

        # create <xmlData> subelement; append @metadata tree.
        xmlData_el = etree.SubElement(mdWrap_el, "{" + self.ns_map[self.prefix] + "}xmlData",
                nsmap=self.ns_map)
        xmlData_el.append(metadata)

        return mdWrap_el


# TEST.
def main():
    
    from mets_ns import ns_map
    from dcxml import simpledc

    # create Dublin Core tree.
    md = dict(titles = ["Test"],
            descriptions = ["A test."])
    md = simpledc.dump_etree(md)

    # wrap Dublin Core.
    mdwrap_el = MdWrap("mets", ns_map)
    mdwrap_el = mdwrap_el.mdWrap(md, "DC", {"ID":"Test_Metadata"})
    return mdwrap_el


if __name__ == "__main__":
    
    mdwrapx = main()

    # print XML.
    mdwrapx = etree.tostring(mdwrapx, pretty_print=True)
    mdwrapx = mdwrapx.decode("utf-8")
    print(mdwrapx)


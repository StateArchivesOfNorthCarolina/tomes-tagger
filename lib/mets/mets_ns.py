#!/usr/bin/env python3

""" This file contains constant METS namespace values for import by other modules. """

# set namespace map.
ns_map = {"mets" : "http://www.loc.gov/METS/",
        "xlink" : "http://www.w3.org/1999/xlink"}

# makes namespace URIs callable via prefix label.
def ns_id(prefix):
    prefix = ns_map[prefix]
    uri_prefix = "{" + prefix + "}"
    return uri_prefix

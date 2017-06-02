#!/usr/bin/env python3

""" Simple test to see if valid METS can be made with the modules. """

# import modules.
import agent
import div
import fileGrp
import mdWrap
import mets_ns
from mdSecType import MdSecType
from lxml import etree

# pre-built test sections.
agentx = agent.main()
mdwrapx = mdWrap.main()
filegrpx = fileGrp.main()
divx = div.main()

# mdSecType builder.
mdSecTyper = MdSecType("mets", mets_ns.ns_map)

# <mets>
mets_el = etree.Element("{" + mets_ns.ns_map["mets"] + "}mets", nsmap=mets_ns.ns_map)

# <metsHdr>
metshdr_el= etree.SubElement(mets_el, "{" + mets_ns.ns_map["mets"] + "}metsHdr",
        nsmap=mets_ns.ns_map)
metshdr_el.append(agentx)

# <dmdSec>
#dmdsec_el= etree.SubElement(mets_el, "{" + mets_ns.ns_map["mets"] + "}dmdSec",
        #nsmap=mets_ns.ns_map)
#dmdsec_el.set("ID", "ID_dmdSec")
dmdsec_el = mdSecTyper.mdSecType("dmdSec", "dmd1")
dmdsec_el.append(mdwrapx)
mets_el.append(dmdsec_el)

# <fileSec>
filesec_el= etree.SubElement(mets_el, "{" + mets_ns.ns_map["mets"] + "}fileSec",
        nsmap=mets_ns.ns_map)
filesec_el.append(filegrpx)

# <structMap>
structmap_el= etree.SubElement(mets_el, "{" + mets_ns.ns_map["mets"] + "}structMap",
        nsmap=mets_ns.ns_map)
structmap_el.append(divx)

# print METS XML.
metsx = etree.tostring(mets_el, pretty_print=True)
metsx = metsx.decode("utf-8")
print(metsx)


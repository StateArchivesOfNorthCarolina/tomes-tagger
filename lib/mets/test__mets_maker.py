#!/usr/bin/env python3

""" Simple test to see if valid METS can be made with the modules. """

# import modules.
import agent
import div
import fileGrp
import mdWrap
import mets_ns
from lxml import etree

# pre-built sections.
agentx = agent.main()
mdwrapx = mdWrap.main()
filegrpx = fileGrp.main()
divx = div.main()

# <mets>
mets_el = etree.Element(mets_ns.ns_id("mets") + "mets", nsmap=mets_ns.ns_map)

# <metsHdr>
metshdr_el= etree.SubElement(mets_el, mets_ns.ns_id("mets") + "metsHdr", nsmap=mets_ns.ns_map)
metshdr_el.append(agentx)

# <dmdSec>
dmdsec_el= etree.SubElement(mets_el, mets_ns.ns_id("mets") + "dmdSec", nsmap=mets_ns.ns_map)
dmdsec_el.set("ID", "ID_dmdSec")
dmdsec_el.append(mdwrapx)

# <fileSec>
filesec_el= etree.SubElement(mets_el, mets_ns.ns_id("mets") + "fileSec", nsmap=mets_ns.ns_map)
filesec_el.append(filegrpx)

# <structMap>
structmap_el= etree.SubElement(mets_el, mets_ns.ns_id("mets") + "structMap", nsmap=mets_ns.ns_map)
structmap_el.append(divx)

# print METS XML.
metsx = etree.tostring(mets_el, pretty_print=True)
metsx = metsx.decode("utf-8")
print(metsx)

"""
Notepad++ validation against schema isn't liking the CDATA in <FLocat>.
Need to see if this is really a problem.
If so, filenames with ampersands, etc. will get escaped in the element value if not wrapped in CDATA.

... but OTHERWISE ... it's working! :-] 


	Validation of current file using XML schema:


	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
	ERROR: Element '{http://www.loc.gov/METS/}FLocat': Character content is not allowed, because the content type is empty.
"""





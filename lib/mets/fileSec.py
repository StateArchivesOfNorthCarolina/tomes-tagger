"""
attachments = fileSec.fileGrp(directory="./myDir", id_prefix="attachments_")
attachments.xml("attachments")
"""

#
import hashlib
import os
from datetime import datetime


#
def get_mime(f):
    mimes = {".xml": "application/xml"}
    ext = os.path.splitext(f)[1]
    mime = mimes.get(ext)
    return mime


#
def fileGrp(directory, id_prefix):
    
    i = 0
    fileGrp = {}
    for root, dirs, files in os.walk(directory + "/attachments"):
        
        for myfile in files:

            flocat = os.path.join(root, myfile)
            with open(flocat, "rb") as f:
                checksum = hashlib.sha256()
                checksum.update(f.read())
                file_checksum = checksum.hexdigest()

            # "The number of seconds can include decimal digits to arbitrary precision." per: https://www.w3.org/TR/xmlschema-2/
            file_created = os.path.getctime(flocat)
            file_created = datetime.utcfromtimestamp(file_created).isoformat() 
            
            flocat_loctype = flocat.replace(directory, "")
            flocat_loctype = flocat_loctype.replace("\\", "/")
            fileGrp[flocat] = {"file":
                                    {"@ID": id_prefix + str(i).zfill(5),
                                    "@CHECKSUM": file_checksum,
                                    "@CHECKSUMTYPE": "SHA-256",
                                    "@CREATED": file_created,
                                    "@MIMETYPE": get_mime(flocat),
                                    "@SIZE": os.path.getsize(flocat),
                                    "FLocat": 
                                        ({"@LOCTYPE": "OTHER"},
                                        flocat_loctype)
                                    }
                                }
            i += 1
            #break

        return fileGrp
   
testDir = open(".testDir").read()
results = fileGrp(testDir, "attachments_")
import json
results = json.dumps(results, indent=2)
print(results)

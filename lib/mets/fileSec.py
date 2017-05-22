import datetime
import hashlib
import os

def attachments(r):
    ID = None
    CHECKSUM = None
    CHECKSUMTYPE = "SHA-256"
    CREATED = None
    MIMETYPE = "attachment/xml"
    SIZE = None

    files_dict = {}
    i = 0
    for root, dirs, files in os.walk(r + "/attachments"):
        
        for name in files:
            name = os.path.join(root, name)
            
            ID = "attachment_" + str(i).zfill(5)
            
            with open(name):
                m = hashlib.sha256()
                fr = open(name, "rb").read()
                m.update(fr)
                CHECKSUM = m.hexdigest()
            
            SIZE = os.path.getsize(name)
            CREATED = os.path.getctime(name)

            # "The number of seconds can include decimal digits to arbitrary precision." per: https://www.w3.org/TR/xmlschema-2/
            CREATED = datetime.datetime.utcfromtimestamp(CREATED).isoformat() 
            
            files_dict[name] = {"ID": ID,
                                "CHECKSUM": CHECKSUM,
                                "CREATED": CREATED,
                                "SIZE": SIZE}
            break

        return files_dict
        
a = attachments()
print(a)

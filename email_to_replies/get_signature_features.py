import re

SIGNATURE = None
ADDRESS = None

def _hasEmail():
    if ADDRESS == None:
        x = False
    else:
        x = ADDRESS in SIGNATURE
    return int(x)

def _countPhones():
    pattern = "[\(]{0,1}[2-9][0-9]{2}[)-.][ ]{0,1}[0-9]{3}[-.][0-9]{4}"
              # pattern based on: http://regexlib.com/REDetails.aspx?regexp_id=22
    x = re.findall(pattern, SIGNATURE)
    return len(x)

def _countZips():
    pattern = "[0-9]{5}(\n|-[0-9]{4})\n"
    x = re.findall(pattern, SIGNATURE)
    return len(x)

def _countQuotes():
    pattern = "\"[\w]+[\.\?!]\""
    x = re.findall(pattern, SIGNATURE)
    return len(x)

def _countURLs():
    pattern = "((http|https)\://|www\.)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(:[a-zA-Z0-9]*)?/?([a-zA-Z0-9\-\._\?\,\'/\\\+&amp;%\$#\=~])*"
              # pattern based on: http://regexlib.com/REDetails.aspx?regexp_id=146
    x = re.findall(pattern, SIGNATURE)
    return len(x)
    
def _countLines():
    x = SIGNATURE.split("\n")
    return len(x)

#####
def getFeatures(tests=[_hasEmail,
                       _countPhones,
                       _countZips,
                       _countQuotes,
                       _countURLs,
                       _countLines]):
    features = [t() for t in tests]
    return features

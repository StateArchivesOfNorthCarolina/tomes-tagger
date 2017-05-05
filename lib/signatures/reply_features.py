# import modules.
import re

class Features():

    """ A feature extractor class for email replies.
    
    Attributes:
        self.signature (str): An email signature block.
        self.sender_address (str): The email address for the signature's author.

    Example:
        >>> import reply_features as rf
        >>> dupin = rf.Features("C. Auguste Dupin\nPrivate Investigator",
                                "c.dupin@stories.poe")
        >>> dupin.get_features()
        {'hasEmail': 0, 'countPhones': 0, 'countZips': 0, 'countQuotes': 0, 'countURLs': 0,
        'countLines': 2}
        >>> dupin.get_feature_vector()
        [0, 0, 0, 0, 0, 2]
    """

    def __init__(self, signature, sender_address):
        """ Sets instance attributes.

        Args:
            signature (str): An email signature block.
            sender_address (str): The email address for the signature's author.
        """
        self.signature = signature
        self.sender_address = sender_address


    def _hasEmail(self):
        """ Returns 1 if sender_address is present in self.signature.
            Otherwise, returns 0.
        """
        if self.sender_address == None:
            x = False
        else:
            x = self.sender_address in self.signature
        return int(x)

    
    def _countPhones(self):
        """ Returns integer count for phone/fax number patterns in self.signature. """

        pattern = "[\(]{0,1}[2-9][0-9]{2}[)-.][ ]{0,1}[0-9]{3}[-.][0-9]{4}"
                  # pattern based on: http://regexlib.com/REDetails.aspx?regexp_id=22
        x = re.findall(pattern, self.signature)
        return len(x)

    
    def _countZips(self):
        """ Returns integer count for zipcode number patterns in self.signature. """
        
        pattern = "[0-9]{5}(\n|-[0-9]{4})\n"
        x = re.findall(pattern, self.signature)
        return len(x)

    
    def _countQuotes(self):
        """ Returns integer count for double-quoted string patterns in self.signature. """

        pattern = "\"[a-zA-Z0-9\s]{10,140}[.?!]\""
                  # 140 character limit inspired by Twitter and after consulting:
                  # https://strainindex.wordpress.com/2008/07/28/the-average-sentence-length/
        x = re.findall(pattern, self.signature)
        return len(x)

    
    def _countURLs(self):
        """ Returns integer count for HTTP/HTTPS URL patterns in self.signature. """

        pattern = "((http|https)\://|www\.)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(:[a-zA-Z0-9]*)?/?([a-zA-Z0-9\-\._\?\,\'/\\\+&amp;%\$#\=~])*"
                  # pattern based on: http://regexlib.com/REDetails.aspx?regexp_id=146
        x = re.findall(pattern, self.signature)
        return len(x)
        
    
    def _countLines(self):
        """ Returns integer count for number of lines in self.signature. """

        x = self.signature.split("\n")
        return len(x)

    
    def get_features(self, tests=[_hasEmail,
                                  _countPhones,
                                  _countZips,
                                  _countQuotes,
                                  _countURLs,
                                  _countLines]):
        """ Returns dictionary for all test results with test names as keys. """

        feature_dict = {}
        for test in tests:
            test_name = test.__name__
            test_name = test_name[1:]
            feature_dict[test_name] = test(self)
        return feature_dict


    def get_feature_vector(self):
        """ Returns a list of values only for self.get_features(). """
        
        feature_vector = [f for f in self.get_features().values()]
        return feature_vector


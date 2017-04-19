#!/usr/bin/env python3

"""
TODO:
    - I still get a Windows/"file in use" error every now and then even with the __del__
    method. Maybe I should just remove that method and let the file stick around?
    Alternatively, create an self.array of used Temporary Files and delete each one with
    __del__()?
"""

# import modules.
import codecs
import os
import subprocess
import tempfile
from bs4 import BeautifulSoup


class Lynx():

    """ A class to convert HTML files OR strings to plain text via the Lynx browser.
    For more information about Lynx, see: http://lynx.browser.org. """
    
    def __init__(self, custom_options={}):

        """ Sets instance attributes.
        
        Args:
            custom_options: ???
        """

        # default options for Lynx.
        options = {"nolist":True, "nomargins":True}
        
        # add custom options.
        for key, val in custom_options.items():
            options[key] = val
        self.options = options
        self.options = [key for key, val in options.items() if val]
        self.options.append("dump")

        # persistent temporary file name.
        self.html_file = "_tmp.html"


    def __del__(self):


        """ Removes temporary file if it exists. """
        pass
        #if os.path.isfile(self.html_file):
        #    os.remove(self.html_file)

    
    def to_text(self, html, charset="utf-8"):

        """ Converts HTML files OR strings to plain text via the Lynx browser.

        Args:
            html (str):
            charset (str):

        Examples:

        """

        # create beginning Lynx command line snippet.
        args = "lynx -"
        args += " -".join(self.options)

        # if @html is not a file, write data to temporary file.
        # complete Lynx command line snippet.
        if not os.path.isfile(html):
            with codecs.open(self.html_file, "w", encoding=charset) as tmp:
                tmp.write(html)
            args += " " + self.html_file
        else:
            args += " " + html

        # run Lynx.
        cmd = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # return stdout.
        if cmd.returncode == 0:
            stdout = cmd.stdout.decode(encoding=charset)
        else:
            stdout = None

        return stdout

#
def main():
    lynx = Lynx(custom_options={})
    print(lynx.to_text("testLists.html"))
    print(lynx.to_text("<ul><li>foo</li></ul>"))
    print(lynx.to_text("testLists.html"))

if __name__ == "__main__":
    main()

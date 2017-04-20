#!/usr/bin/env python3

"""
TODO:
    - ???
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
    
    def __init__(self, custom_options={}, temp_file="_tmp.html"):

        """ Sets instance attributes.
        
        Args:
            custom_options (dict): 
            temp_file (str): 
        """

        # set default options for Lynx.
        options = {"nolist":True, "nomargins":True}
        
        # add in custom options.
        for key, val in custom_options.items():
            options[key] = val
        self.options = options
        self.options = [key for key, val in options.items() if val]
        self.options.append("dump")

        # set persistent temporary file name.
        self.temp_file = temp_file


    def __del__(self):

        """ Trys to remove temporary file if it exists. Passes on permission error. """
        if os.path.isfile(self.temp_file):
            try:
                os.remove(self.temp_file)
            except PermissionError:
                pass


    def to_text(self, html, is_raw=False, charset="utf-8"):

        """ Converts HTML files OR strings to plain text via the Lynx browser.

        Args:
            html (str):
            is_raw (bool):
            charset (str):

        Examples:

        """
    
        # create beginning Lynx command line snippet.
        args = "lynx -"
        args += " -".join(self.options)

        # if @html is an HTML string, write data to temporary file.
        if is_raw:
            with codecs.open(self.temp_file, "w", encoding=charset) as tmp:
                tmp.write(html)
            args += " " + self.temp_file
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


def main():
    lynx = Lynx(custom_options={})
    print(lynx.to_text("testLists.html"))
    print("-----")
    print(lynx.to_text("<ul><li>foo</li></ul>", is_raw=True))


if __name__ == "__main__":
    main()

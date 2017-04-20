#!/usr/bin/env python3

# import modules.
import codecs
import os
import subprocess
import tempfile
from bs4 import BeautifulSoup


class BeautifulSoup_TOMES(BeautifulSoup):

    def shift_links(self):
        """ Appends A.href value to A tag's text for A tags in BeautifulSoup instance.
            i.e. <a href="bar">foo</a> to <a href="bar">foo [bar]</a>
        """

        a_tags = self.find_all("a")
        for a_tag in a_tags:
            if "href" not in a_tag.attrs:
                continue
            href = a_tag["href"]
            text = a_tag.string + " [" + href + "]"  
            a_tag.string.replace_with(text)

        return self


    def remove_images(self):
        """ Removes image tags from BeautifulSoup instance. """

        img_tags = self.find_all("img")
        for img_tag in img_tags:
            img_tag.extract()

        return self


class Lynx():

    """ A class to convert HTML files OR strings to plain text via the Lynx browser.
    For more information about Lynx, see: http://lynx.browser.org.
    """
    
    def __init__(self, custom_options={}, temp_file="_tmp.html"):

        """ Sets instance attributes.
        
        Args:
            custom_options (dict): Custom Lynx options per:
                http://lynx.browser.org/lynx2.8.8/breakout/lynx_help/Lynx_users_guide.html#InteractiveOptions
                Retrieved: April 2017.
            temp_file (str): File in which to store raw HTML strings as Lynx only converts files.
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
            html (str): The HTML file OR the raw HTML string to convert to text.
            is_raw (bool): If True, @html is saved to self.temp_file prior to conversion.
            charset (str): The encoding for the converted text.

        Examples:
            >>> lynx.to_text("testLists.html")
            # returns plain text version of "testLists.html".
            >>> lynx.to_text("<p class='hi'>Hello World!</p>", is_raw=True)
            '\nHello World!\n\n'
        """
    
        # create beginning Lynx command line snippet.
        args = "lynx -"
        args += " -".join(self.options)

        # if @is_raw == True, write @html to temporary file.
        # complete command line snippet.
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

# TESTS.
def main():
    lynx = Lynx(custom_options={})
    print(lynx.to_text("testLists.html"))
    print("-----")
    print(lynx.to_text("<p class='hi'>Hello World!</p>", is_raw=True))
    print("-----")
    html = open("test.html").read()
    soup = BeautifulSoup_TOMES(html, "html5lib")
    soup.shift_links()
    soup.remove_images()
    print(lynx.to_text(str(soup), is_raw=True))

if __name__ == "__main__":
    main()

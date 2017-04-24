#!/usr/bin/env python3

""" This module has classes for converting HTML strings and files to plain text versions. """

# import modules.
import codecs
import os
import subprocess
from bs4 import BeautifulSoup


class ModifyHTML(BeautifulSoup):
    """ A class with tools to modify the HTML DOM via BeautifulSoup.
    
    Example:
        >>> html = open("sample.html").read() # string
        >>> html = ModifyHTML(html, "html5lib") #BeautifulSoup object
        >>> html.shift_links() # alters DOM
        >>> html.remove_images() # alters DOM
        >>> html.raw() # back to string ...
    """


    def shift_links(self):
        """ Appends A.href value to A tag's text for A tags in BeautifulSoup instance.
            i.e. <a href="bar">foo</a> to <a href="bar">foo [bar]</a>
        """

        a_tags = self.find_all("a")
        for a_tag in a_tags:
            if a_tag.string == None:
                continue
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


    def raw(self):
        """ Returns string version of BeautifulSoup instance. """

        return str(self)


class HtmlToText():

    """ A class to convert HTML files OR strings to plain text via the Lynx browser. """
    
    def __init__(self, custom_options=None, temp_file="_tmp.html"):

        """ Sets instance attributes.
        
        Args:
            - custom_options (dict): Custom Lynx options per: http://lynx.browser.org/lynx2.8.8/breakout/lynx_help/Lynx_users_guide.html#InteractiveOptions (Retrieved: April 2017).
            - temp_file (str): File in which to store raw HTML strings.
        """

        # set default options for Lynx.
        options = {"nolist":True, "nomargins":True, "dump":True}

        # add in custom options.
        if isinstance(custom_options, dict): 
            for key, val in custom_options.items():
                options[key] = val
        self.options = options

        # set persistent temporary file name.
        self.temp_file = temp_file


    def __del__(self):

        """ Trys to remove temporary file if it exists. Passes on permission error. """
        if os.path.isfile(self.temp_file):
            try:
                os.remove(self.temp_file)
            except PermissionError:
                pass


    def text(self, html, is_raw=False, charset="utf-8"):

        """ Converts HTML files OR strings to plain text via the Lynx browser.

        Args:
            - html (str): The HTML file OR the raw HTML string to convert to text.
            - is_raw (bool): If True, @html is saved to self.temp_file prior to conversion.
            - charset (str): The encoding for the converted text.

        Examples:
            >>> h2t = HtmlToText()
            >>> ht2.text("sample.html")
            # returns plain text version of "sample.html".
            >>> ht2.text("<p class='hi'>Hello World!</p>", is_raw=True)
            '\nHello World!\n\n'
        """
    
        # create beginning Lynx command line snippet.
        arg_options = [key for key, val in self.options.items() if val]
        args = "lynx -"
        args += " -".join(arg_options)

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
            stdout = cmd.stdout.decode(encoding=charset, errors="backslashreplace")
        else:
            stdout = None

        return stdout



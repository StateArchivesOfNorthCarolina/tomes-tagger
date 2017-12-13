#!/usr/bin/env python3

""" This module contains classes for manipulating HTML and converting HTML to plain text. """

# import modules.
import codecs
import logging
import os
import subprocess
from bs4 import BeautifulSoup
import platform

if platform.system() == "Windows":
    lynx_exec = "C:\Program Files (x86)\lynx\lynx.exe"

if platform.system() == "Linux":
    lynx_exec = "lynx"


class ModifyHTML():
    """ A class with tools to modify the HTML DOM via BeautifulSoup.
    
    Example:
        >>> html = open("sample.html").read() # string.
        >>> html = ModifyHTML(html, "html5lib") #BeautifulSoup object.
        >>> html.shift_links()
        >>> html.remove_images()
        >>> html.raw() # string version of the HTML with shifted links and no images.
    """


    def __init__(self, html, parser="html5lib"):
        """ Sets instance attributes. """

        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # compose BeautifulSoup object.
        self.root = BeautifulSoup(html, parser)


    def shift_links(self):
        """ Appends each A tag's @href value to the tag's text value if the @href value starts
        with "http" or "https", i.e. "<a href='bar'>foo</a>" to "<a href='bar'>foo [bar]</a>".

        Returns:
            None
        """

        self.logger.info("Shifting @href values to parent <a> tags.")

        # get all A tags.
        a_tags = self.root.find_all("a")
        
        # append @href values to text values.
        for a_tag in a_tags:
            
            if a_tag.string is None:
                continue
            if "href" not in a_tag.attrs:
                continue
            
            # get @href; ignore non-http|https values. 
            href = a_tag["href"]
            if href[0:4].lower() == "http": # case insensitive.
                text = a_tag.string + " [" + href + "]"  
                a_tag.string.replace_with(text)

        return


    def remove_images(self, preserve_alt=False):
        """ Removes image tags from DOM.

        Args:
            - preserve_alt (bool): If True, the "alt" attribute in the <img> tag will be 
            extracted and placed in a new and adjacent <span> tag to preserve the attribute 
            value.
        
        Returns:
            None
        """
        
        self.logger.info("Removing image tags.")
        
        # get all image tags; remove them.
        img_tags = self.root.find_all("img")
        for img_tag in img_tags:
            if preserve_alt:
                if "alt" in img_tag.attrs and img_tag["alt"] != "":
                    span = BeautifulSoup.new_tag(self.root, "span")
                    span.string = "[IMAGE: " + img_tag["alt"] + "]"
                    img_tag.insert_after(span)
            img_tag.extract()

        return


    def raw(self):
        """ Returns string version of current DOM.
        
        Returns:
            str: The return value.
        """

        self.logger.debug("Converting BeautifulSoup object to HTML string.")
        strroot = str(self.root)
        return strroot


class HTMLToText():
    """ A class to convert HTML files OR strings to plain text via the Lynx browser.
    
    Examples:
    >>> h2t = HTMLToText()
    >>> h2t.text("sample.html") # returns plain text version of "sample.html"
    >>> ht2.text("<p class='hi'>Hello World!</p>", is_raw=True)
    '\nHello World!\n\n'
    """
    
    def __init__(self, custom_options=None, temp_file=os.path.join(os.getcwd(), "_tmp.html")):
        """ Sets instance attributes.
        
        Args:
            - custom_options (dict): Custom Lynx options per: http://lynx.browser.org/lynx2.8.8/breakout/lynx_help/Lynx_users_guide.html#InteractiveOptions (Retrieved: April 2017).
            - temp_file (str): File in which to store raw HTML strings.
        """

        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set default options for Lynx.
        options = {"nolist":True, "nomargins":True, "dump":True}

        # add in custom options.
        if isinstance(custom_options, dict):
            for key, val in custom_options.items():
                options[key] = val
        self.options = options

        # set persistent temporary file name.
        self.temp_file = os.path.abspath(temp_file)


    def __del__(self):
        """ Trys to remove temporary file if it exists. Passes on permission error. """

        if os.path.isfile(self.temp_file):
            try:
                self.logger.debug("Removing temporary HTML file: {}".format(self.temp_file))
                os.remove(self.temp_file)
            except PermissionError:
                self.logger.warning("Unable to remove temporary file: {}".format(
                    self.temp_file))
                pass

    def text(self, html, is_raw=False, charset="utf-8"):
        """ Converts HTML files OR strings to plain text string via the Lynx browser.

        Args:
            - html (str): The HTML file OR the raw HTML string to convert to text.
            - is_raw (bool): If True, @html is saved to self.temp_file prior to conversion.
            - charset (str): The encoding for the converted text.

        Returns:
            str: The return value.
        """
    
        self.logger.info("Converting HTML to plain text.")

        # create beginning Lynx command line snippet.
        arg_options = [key for key, val in self.options.items() if val]
        args = []
        args.append(lynx_exec)
        for opt in arg_options:
            args.append("-{}".format(opt))


        # if @is_raw == True, write @html to temporary file.
        # complete command line snippet.
        if is_raw:
            self.logger.debug(
                    "Writing HTML to temporary HTML file: {}".format(self.temp_file))
            with codecs.open(self.temp_file, "w", encoding=charset) as tmp:
                tmp.write(html)
            #args += " " + self.temp_file
            args.append(self.temp_file)
        else:
            #args += " " + html
            args.append(html)

        # run Lynx.
        self.logger.debug("Converting HTML to text via: '{}'".format(args))
        text = html
        try:
            cmd = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            text = cmd.stdout.decode(encoding=charset, errors="backslashreplace")
        except FileNotFoundError as err:
            self.logger.error(err)
            self.logger.error(html)

        # return stdout.

        return text


if __name__ == "__main__":    
    pass


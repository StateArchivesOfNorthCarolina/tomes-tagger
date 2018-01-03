#!/usr/bin/env python3

""" This module contains classes for manipulating HTML and converting HTML to plain text. """

# import modules.
import codecs
import logging
import os
import shutil
import subprocess
import tempfile
from bs4 import BeautifulSoup
from datetime import datetime


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
        """ Appends each <a> tag's "href" attribute value to the tag's text value if the 
        value starts with "http" or "https", i.e. "<a href='bar'>foo</a>" to 
        "<a href='bar'>foo [bar]</a>".

        Returns:
            None
        """

        self.logger.info("Shifting @href values to parent <a> tags.")

        # get all <a> tags.
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

        self.logger.info("Converting BeautifulSoup object to HTML string.")
        strroot = str(self.root)
        return strroot


class HTMLToText():
    """ A class to convert HTML files OR strings to plain text via the Lynx browser.
    
    Examples:
    >>> h2t = HTMLToText()
    >>> h2t.get_text("sample.html") # returns plain text version of "sample.html"
    >>> ht2.get_text("<p class='hi'>Hello World!</p>", is_raw=True)
    '\nHello World!\n\n'
    """
    
    def __init__(self, lynx_options=None):
        """ Sets instance attributes.
        
        Args:
            - lynx_options (dict): Any additional Lynx command line options for the
            "dump" command. See: "http://goo.gl/e55eNp" (Retrieved January 3, 2018). 
        """

        # set logger; suppress logging by default. 
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

        # set default and custom options for Lynx.
        self.lynx_options = {"nolist":True, "nomargins":True}
        if isinstance(lynx_options, dict):
            for key, val in lynx_options.items():
                self.lynx_options[key] = val
        self.lynx_options["dump"] = True

        # ???
        self.temp_dir = self.__make_temp_dir()


    def __make_temp_dir(self):
        """ ??? 
        
        Returns:
            tempfile.TemporaryDirectory ???
        """

        # ???
        temp_dir = os.path.dirname(os.path.abspath(__file__))
        temp_dir = os.path.join(temp_dir, "_temp")
        
        # ???
        if not os.path.isdir(temp_dir):
            try:
                self.logger.info("???")
                os.mkdir(temp_dir)
            except Exception as err:
                self.logger.error(err)
                self.logger.warning("???")
                # ???

        temp_dir =tempfile.TemporaryDirectory(dir=temp_dir)
        return temp_dir


    def __del__(self):
        """ Trys to remove temporary ???
        """

        # ???
        try:
            self.logger.info("Removing temporary folder: {}".format(self.temp_dir.name))
            self.temp_dir.cleanup()
        except Exception as err:
            self.logger.error(err)
            self.logger.warning("Unable to completely remove temporary folder.")
            self.logger.info("Attempting fallback method to clean up temporary folder.")
            shutil.rmtree(self.temp_dir.name, ignore_errors=True)
            
            # ???
            if os.path.isdir(self.temp_dir.name):
                self.logger.info("Please manually delete: {}".format(self.temp_dir.name))
            else:
                self.logger.info("Success; temporary folder finally removed.")
            
    
    def get_text(self, html, is_raw=False, charset="utf-8"):
        """ Converts HTML files OR strings to plain text string via the Lynx browser.

        Args:
            - html (str): The HTML file OR the raw HTML string to convert to text.
            - is_raw (bool): If True, @html is saved to self.temp_file prior to conversion.
            - charset (str): The encoding for the converted text.

        Returns:
            str: The return value.
        """
    
        self.logger.info("Converting HTML to plain text.")

        # create beginning Lynx command line snippet; add options. ???
        args = ["lynx"]
        options = [key for key, val in self.lynx_options.items() if val]        
        for option in options:
            args.append("-{}".format(option))

        # if @is_raw == True, write @html to temporary file.
        # complete command line snippet.
        if is_raw:
            temp_file = os.path.join(self.temp_dir.name, 
                    datetime.utcnow().strftime("%Y%m%d_%H-%M-%S-%f") + ".html")
            self.logger.info("Writing HTML to temporary HTML file: {}".format(temp_file))
            with codecs.open(temp_file, "w", encoding=charset) as tf:
                tf.write(html)
            args.append(temp_file)
        else:
            args.append(html)

        # run Lynx; capture its output.
        self.logger.debug("Converting HTML to text via: '{}'".format(" ".join(args)))
        try:
            cmd = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                    check=True)
            text = cmd.stdout.decode(encoding=charset, errors="backslashreplace")
        except FileNotFoundError as err:
            self.logger.error(err)
            self.logger.warning("Couldn't convert HTML. Is Lynx installed correctly?")
            self.logger.warning("Falling back to empty string.")
            text = ""
        
        # return HTML to text conversion.
        return text


if __name__ == "__main__":    
    pass


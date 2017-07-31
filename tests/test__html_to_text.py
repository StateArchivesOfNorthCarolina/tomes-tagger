#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import logging
import unittest
from lib.html_to_text import *


class Test_HTMLToText(unittest.TestCase):


    def setUp(self):

        # enable logging.
        logging.basicConfig(level=logging.WARNING)
        
	# set attributes.
        self.h2t = HTMLToText()
        self.sample = "<html><head></head><body><a href=\"http://h.w\">{}</a></body></html>"
    
    
    def test__shift_links(self):
        """ Does extracting a.@href values into body text work? """

        # format sample text.
        html = self.sample.format("Hello World!")
        
        # remove links.
        html = ModifyHTML(html)
        html.shift_links()
        html = html.raw()

        # check if result is as expected.
        expected = self.sample.format("Hello World! [http://h.w]")
        self.assertEqual(html, expected)

    
    def test__remove_images(self):
        """ Does removing image tags work? """
        
        # add image tag to sample text.
        img = "Hello World!<img src='hw.jpg' alt='Hello World!'>"
        html = self.sample.format(img)
        
        # remove images.
        html = ModifyHTML(html)
        html.remove_images()
        html = html.raw()
        
        # check if result is as expected. 
        expected = self.sample.format("Hello World!")
        self.assertEqual(html, expected)

    
    def test__html_to_text(self):
        """ Does HTML to text conversion work? """
        
        # format sample text.
        html = self.sample.format("Hello World!")
        
        # convert to plain text.
        plain = self.h2t.text(html, is_raw=True)
        
        # check if result is as expected.
        expected = "\nHello World!\n\n"
        self.assertEqual(plain, expected)


# CLI TEST.
def main(html: "HTML file"):
    
    "Prints plain text version of an HTML document.\
    \nexample: `py -3 test__html_to_text sample_files\sampleHTML.html`"

    # read HTML file.
    html = open(html).read()
    
    # modify HTML.
    html = ModifyHTML(html)
    html.shift_links()
    html.remove_images()
    html = html.raw()

    # convert to plain text.
    h2t = HTMLToText()
    plain = h2t.text(html, is_raw=True)
    print(plain)


if __name__ == "__main__":
    
    import plac
    plac.call(main)


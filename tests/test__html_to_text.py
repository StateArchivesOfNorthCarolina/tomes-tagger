#!/usr/bin/env python3

# import modules.
import sys; sys.path.append("..")
import unittest
from lib.html_to_text import *

class Test_HTMLToText(unittest.TestCase):

    def setUp(self):

        self.H2T = HTMLToText()
        self.HTML = "<html><head></head><body><a href=\"http://h.w\">{}</a></body></html>"
    
    def test__shift_link(self):

        html = self.HTML.format("Hello World!")
        html = ModifyHTML(html, "html5lib")
        html.shift_links()
        html = html.raw()
        expected = self.HTML.format("Hello World! [http://h.w]")
        self.assertEqual(html, expected)

    def test__remove_images(self):

         img = "Hello World!<img src='hw.jpg' alt='Hello World!'>"
         html = self.HTML.format(img)
         html = ModifyHTML(html, "html5lib")
         html.remove_images()
         html = html.raw()
         html2 = self.HTML.format("Hello World!")
         self.assertEqual(html, html2)

    def test__text(self):
        
        html = self.HTML.format("Hello World!")
        plain = self.H2T.text(html, is_raw=True)
        expected = "\nHello World!\n\n"
        self.assertEqual(plain, expected)


if __name__ == "__main__":
    
    unittest.main()


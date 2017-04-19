#!/usr/bin/env python3

# import modules.
import subprocess
import tempfile
from bs4 import BeautifulSoup

class Lynx():
    
    def __init__(self, encoding="utf8", custom_options={}):

        # default options for Lynx.
        options = {"nolist":True, "nomargins":True}
        
        # add custom options.
        for key, val in custom_options.items():
            options[key] = val
        self.options = options
        self.options = [key for key, val in options.items() if val]
        self.options.append("dump")

    def to_text(self, html_file, encoding="utf-8"):

        args = "lynx -"
        args += " -".join(self.options)
        args += " " + html_file
        cmd = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(cmd)
        if cmd.stderr.decode() == "":
            stdout = cmd.stdout.decode(encoding=encoding)
        else:
            stdout = None
        return stdout

def main():
    lynx = Lynx(custom_options={})
    print(lynx.to_text("testLists.html"))

if __name__ == "__main__":
    main()

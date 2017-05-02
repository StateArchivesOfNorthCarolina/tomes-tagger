#!/usr/bin/env python3

"""
TODO:
    - refactor code; fix issues/errors raised by pylint.
    - replace custom _arg_parse with argparse module.
    - self.argparse() should only run if command line is used (not if class is imported).
    - define @filename and @logger in "__init__"?
    - if "logging" is even needed, does @filename need to be fixed? i.e. if class is instantiated again, isn't "logfile.log" going to be overwritten?
    - have alternative to calling ".exe" file (i.e. if using MAC/Linux).
    - for Windows, check for required DLLs needed by readpst.exe: libiconv2.dll and regex2.dll.
    - looks like DArcMail needs mbox files to end with extension ".mbox"; current output appears to not have any extension.
"""

# import modules.
import logging
import subprocess
import sys


class PstToMbox():
    """ A class to convert a PST file to Mbox format. """

    filename = None
    logger = None
    

    def __init__(self):
        """ Sets logging format and attributes. """

        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logfile.log', filemode='w', level=logging.DEBUG)
        self.logger = logging.getLogger()
        self._arg_parse()
  
    
    def _arg_parse(self):
        """ Gets PST file from command line argument. """
        
        if len(sys.argv) != 2:
            self.logger.critical("PST file not provided.")
            self.logger.critical("Example: 'python pst_to_mbox.py temp.pst'") 
            sys.exit(0)
        self.filename = sys.argv[1]
    
    
    def mbox(self):
        """ Converts PST to Mbox. """
        
        # creates output folder.
        try:
            subprocess.check_call(["mkdir", "mbox"], shell=True)
            self.logger.info("Success: 'mbox' folder created.")
        except subprocess.CalledProcessError as e:
            self.logger.critical(str(e))
            self.logger.critical("Please delete or rename the existing 'mbox' folder first.")
            sys.exit(0)                
        
        # calls readpst to create Mbox.
        try:
            subprocess.call(["readpst.exe", "-o", "mbox", "-r", str(self.filename)], shell=True)
            self.logger.info("Success: pst converted to mbox.")
        except subprocess.CalledProcessError as e:
            self.logger.critical(str(e.output))
        except Exception as e:
            self.logger.critical(str(e))


# Run.
def main():
    p2m = PstToMbox()
    p2m.mbox()

if __name__ == "__main__":
    main()


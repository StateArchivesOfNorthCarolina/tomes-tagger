"""
TO DO:
    - refactor code; fix issues/errors raised by pylint.
    - replace custom _arg_parse with argparse module.
    - reduce logging of errors by catching error type rather than numerous "except" statements.
    - define @filename and @logger in "__init__"?
    - if "logging" is even needed, does @filename need to be fixed? i.e. if class is instantiated again, isn't "logfile.log" going to be overwritten?
    - have alternative to calling ".exe" file (i.e. if using MAC/Linux).
    - for Windows, check for required DLLs needed by readpst.exe: libiconv2.dll and regex2.dll.
	- looks like DArcMail needs mbox files to end with extension ".mbox"; current output appears to not have any extension.
"""

import logging
import subprocess
import sys

class Conversion:

    filename = None
    logger = None
    
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='logfile.log', filemode='w', level=logging.DEBUG)
        self.logger = logging.getLogger()
        self._arg_parse()
  
    def _arg_parse(self):
        if len(sys.argv) != 2:
            self.logger.critical("PST file not provided.")
            self.logger.critical("Provide PST file in argument, for instance, in the cmd line enter :'python pst_to_mbox.py temp.pst' to convert temp.pst file to mbox format.") 
            sys.exit(0)
        self.filename = sys.argv[1]
    
    def startConversion(self):
        try:
            subprocess.check_call(["mkdir", "mbox"], shell=True)
            self.logger.info("Folder successfully created.")
        except subprocess.CalledProcessError as e:
            self.logger.critical(str(e))
            self.logger.critical("Kindly delete the old folder named 'mbox' prior to running this file.")
            sys.exit(0)                
        try:
            subprocess.call(["readpst.exe", "-o", "mbox", "-r", str(self.filename)], shell=True)
            self.logger.info("Successful conversion from pst format to mbox format.")
        except subprocess.CalledProcessError as e:
            self.logger.critical(str(e.output))
        except MemoryError as me:
            self.logger.critical(str(me.output))
        except KeyboardInterrupt as kie:
            self.logger.critical(str(kie.output))
        except AttributeError as ae:
            self.logger.critical(str(ae.output))
        except EOFError as eofe:
            self.logger.critical(str(eofe.output))
        except IOError as ioe:
            self.logger.critical(str(ioe.output))
        except OSError as ose:
            self.logger.critical(str(ose.output))
        except ImportError as ime:
            self.logger.critical(str(ime.output))
        except SystemError as se:
            self.logger.critical(str(se.output))
        except UnicodeEncodeError as uee:
            self.logger.critical(str(uee.output))
        except UnicodeDecodeError as ude:
            self.logger.critical(str(ude.output))
        except UnicodeTranslateError as ute:
            self.logger.critical(str(ute.output))
        except WindowsError as we:
            self.logger.critical(str(we.output))
        except RuntimeError as rte:
            self.logger.critical(str(rte.output))

if __name__ == "__main__":
    p_to_m = Conversion()
    p_to_m.startConversion()

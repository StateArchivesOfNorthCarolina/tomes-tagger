from sys import argv
import sys
import subprocess
import os

class Conversion:
	def __init__(self):
		self.startConversion()
	
	def startConversion(self):
		if len(sys.argv) != 2:
			print "PST file not provided."
			print "Provide PST file in argument, for instance, in the cmd line enter :'python pst_to_mbox.py temp.pst' to convert temp.pst file to mbox format." 
		else:
			try:
				subprocess.check_call(["mkdir","mbox"],shell=True)
				print "Folder successfully created."
			except subprocess.CalledProcessError as e:
				print "Kindly delete the old folder named 'mbox' prior to running this file."
				sys.exit(0)	
			try:
				subprocess.call(["readpst.exe","-o","mbox","-r",str(sys.argv[1])],shell=True)
				print "Successful conversion from pst format to mbox format."
			except subprocess.CalledProcessError as e:
				print e.output
			except MemoryError as me:
				print me.output
			except KeyboardInterrupt as kie:
				print kie.output
			except AttributeError as ae:
				print ae.output
			except EOFError as eofe:
				print eofe.output
			except IOError as ioe:
				print ioe.output
			except OSError as ose:
				print ose.output
			except ImportError as ime:
				print ime.output
			except SystemError as se:
				print se.output
			except UnicodeEncodeError as uee:
				print uee.output
			except UnicodeDecodeError as ude:
				print ude.output
			except UnicodeTranslateError as ute:
				print ute.output
			except WindowsError as we:
				print we.output
			except RuntimeError as rte:
				print rte.output

			
Conversion()


	






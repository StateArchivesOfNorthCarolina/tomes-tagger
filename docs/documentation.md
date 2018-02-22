# Introduction

**TOMES Tool** is part of the [TOMES](https://www.ncdcr.gov/resources/records-management/tomes) project.

It is written in Python.

Its purpose is to create a "tagged" version of an [EAXS](http://www.history.ncdcr.gov/SHRAB/ar/emailpreservation/mail-account/mail-account_docs.html) file(s) - an XML schema for storing email account information.

The tagged version of the EAXS file is meant to contain email messages that have been tagged by Name Entity Recognition (NER) tools. It uses a modified version of the original EAXS format.

...

**TOMES Tool**  is under active development by the [State Archives of North Carolina](http://archives.ncdcr.gov/) in conjunction with the [TOMES Project Team](https://www.ncdcr.gov/resources/records-management/tomes/team). Currently, it is not intended for use other than testing by the project team.


# External Dependencies

TOMES Tool requires the following applications:

- [Python 3+](https://www.python.org/download/releases/3.0/) (using 3.6)
	- See the "./requirements.txt" file for additional module dependencies.
- [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) 3.7+ (using 3.7.0)
	- *We're currently using this for NER tagging.*
	- Please see the CoreNLP documentation for Java and memory requirements, etc.
	- You **must** place the "regexner\_TOMES" directory (found in in the "./tomes\_tool/NLP/stanford_edu/stanford-corenlp-full-2016-10-31" directory) and its files into the CoreNLP directory that contains the master JAR file (~"stanford-corenlp-3.7.0.jar").
- [Lynx](http://lynx.browser.org/) 2.8.8+ (using 2.8.8)
	- *We're currently using this for HTML email to plain text conversion.*
	- The "lynx" command must be executable from any directory on your system.
		- For Windows, this will likely require editing your Environmental Variables "PATH" to include the path to the lynx.exe file.


# Installation
After installing the external dependencies above, you'll need to install some required Python packages.

The required packages are listed in the "./requirements.txt" file and can easily be installed via PIP <sup>[1]</sup>: `pip3 install -r requirements.txt`

You should now be able to use TOMES Tool from the command line or as a locally importable Python module.

If you want to install TOMES Tool as a Python package, do: `pip3 install . -r requirements.txt`

Running `pip3 uninstall tomes_tool` will uninstall the TOMES Tool package.

# Unit Tests
While not true unit tests that test each function or method of a given module or class, basic unit tests help with testing overall module workflows.

Unit tests reside in the "./tomes\_tool/tests" directory and start with "test__".

## Running the tests

To run all the unit tests do <sup>[1]</sup>: `py -3 -m unittest` from within the "./tomes\_tool/tests" directory. 

Specific unit tests of interest:

- `py -3 -m unittest test__html_to_text.py`
	- This primarily tests that Lynx can be called by TOMES Tool.
- `py -3 -m unittest test__eaxs_to_tagged.py`
	- This tests the EAXS to tagged EAXS workflow without actually calling CoreNLP or Lynx.

Of course, you can also test CoreNLP directly by starting it and going to the correct local URL, i.e. "localhost:9003". To save time, it is recommended to only enter *very* short text (e.g. "North Carolina").


## Using the command line

All of the unit tests have command line options.

To see the options and usage examples simply call the scripts with the `-h` option: `py -3 test__[rest of filename].py -h` and try the example.

Sample files are located in the "./tomes\_tool/tests/sample_files" directory.

The sample files can be used with the command line options of some of the unit tests.

# Modules
TOMES Tool consists of two high level modules:

1. tagger.py
	* This creates a "tagged" version of a source EAXS file.
2. entities.py
	* This creates a Stanford CoreNLP compliant version of NER patterns from a source Microsoft Excel file.

Both modules can be used as native Python classes or as command line scripts.

## Using modules with Python
To get started, import a module and run help():

	Python 3.6.0 (v3.6.0:41df79263a11, Dec 23 2016, 08:06:12) [MSC v.1900 64 bit (AM
	D64)] on win32
	Type "help", "copyright", "credits" or "license" for more information.
	>>> from tomes_tool import tagger
	>>> help(tagger)
	>>> from tomes_tool import entities
	>>> help(entities)

## Using tagger.py from the command line

1. Start the CoreNLP server.
	- Until further notice, it is assumed you will run the server on port 9003 with a lengthy timeout:
	
		`cd stanford-corenlp-full-2016-10-31`

     	`java -mx2g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9003 -timeout 50000`
2. From the "./tomes\_tool/tomes\_tool" directory do: `py -3 tagger.py -h` 
3. Try the example help command.

## Using entities.py from the command line
1. From the "./tomes\_tool/tomes\_tool" directory do: `py -3 entities.py -h` 
2. Try the example help command.

-----
*[1] Depending on your system configuration, you might be able to specify "python" and "pip" instead of "py -3" or "pip3" from the command line.*

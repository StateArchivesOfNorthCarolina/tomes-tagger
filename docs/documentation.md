# Introduction
**TOMES Tagger** is part of the [TOMES](https://www.ncdcr.gov/resources/records-management/tomes) project.

It is written in Python.

Its purpose is to create a "tagged" version of an [EAXS](http://www.history.ncdcr.gov/SHRAB/ar/emailpreservation/mail-account/mail-account_docs.html) file(s) - an XML schema for storing email account information.

The tagged version of the EAXS file is meant to contain email messages that have been tagged by Name Entity Recognition (NER) tools. It uses a modified version of the original EAXS format.

# External Dependencies
TOMES Tagger requires the following:

- [Python](https://www.python.org) 3.0+ (using 3.5+)
	- See the "./requirements.txt" file for additional module dependencies.
	- You will also want to install [pip](https://pypi.python.org/pypi/pip) for Python 3.
- [Lynx](http://lynx.browser.org/) 2.8.8+ (using 2.8.8)
	- The "lynx" command must be executable from any directory on your system.
		- For Windows, this will likely require editing your Environmental Variables "PATH" to include the path to the lynx.exe file.
- [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) 3.7+ (using 3.7.0)
	- Please see the CoreNLP documentation for Java and memory requirements, etc.
	- If you want to use the TOMES Project NER mappings, you must place the "regexner\_TOMES" directory (found in the "./NLP/stanford_edu/stanford-corenlp-full-2016-10-31" directory) and its files into the CoreNLP directory that contains the master JAR file (~"stanford-corenlp-3.7.0.jar").

# Installation
After installing the external dependencies above, you'll need to install some required Python packages.

The required packages are listed in the "./requirements.txt" file and can easily be installed via PIP <sup>[1]</sup>: `pip3 install -r requirements.txt`

You should now be able to use TOMES Tagger from the command line or as a locally importable Python module.

If you want to install TOMES Tagger as a Python package, do: `pip3 install . -r requirements.txt`

Running `pip3 uninstall tomes_tagger` will uninstall the TOMES Tagger package.

# Unit Tests
While not true unit tests that test each function or method of a given module or class, basic unit tests help with testing overall module workflows.

Unit tests reside in the "./tests" directory and start with "test__".

## Running the tests
To run all the unit tests do <sup>[1]</sup>: `py -3 -m unittest` from within the "./tests" directory. 

Specific unit tests of interest:

- `py -3 -m unittest test__html_to_text.py`
	- This primarily tests that Lynx can be called by TOMES Tagger.
- `py -3 -m unittest test__eaxs_to_tagged.py`
	- This tests the EAXS to tagged EAXS workflow without actually calling CoreNLP or Lynx.

Of course, you can also test CoreNLP directly by starting it and going to the correct local URL, i.e. "localhost:9003". To save time, it is recommended to only enter *very* short text (e.g. "North Carolina").


## Using the command line
All of the unit tests have command line options.

To see the options and usage examples simply call the scripts with the `-h` option: `py -3 test__[rest of filename].py -h` and try the example.

Sample files are located in the "./tests/sample_files" directory.

The sample files can be used with the command line options of some of the unit tests.

# Modules
TOMES Tagger consists of single-purpose high, level module, **tagger.py**. This creates a tagged version of a source EAXS file. It can be used as native Python class or as command line script.

*Before creating a tagged EAXS file, please make sure that you have free disk space that is approximately 1.5 to 2 times greater than the size of your source EAXS file.*

## Using tagger.py with Python
To get started, import the module and run help():

	>>> from tomes_tagger import tagger
	>>> help(tagger)

To create tagged EAXS files, the CoreNLP server will need to be started (default port = 9003). You can start it manually or use one of the startup scripts (see below).

*Note: docstring and command line examples may reference sample and data files that are NOT included in the installed Python package. Please use appropriate paths to sample and data files as needed.*

## Using tagger.py from the command line
1. Start the CoreNLP server with one of the startup scripts: "./NLP/stanford\_edu/start\_server.[bat|sh]".
2. Open another terminal instance.
3. From the "./tomes\_tagger" directory do: `py -3 tagger.py -h` to see an example command.
3. Run the example command.

-----
*[1] Depending on your system configuration, you might need to specify "python3", etc. instead of "py -3" from the command line. Similar differences might apply for PIP.*

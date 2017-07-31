# Introduction

**TOMES Tool** is part of the [TOMES](https://www.ncdcr.gov/resources/records-management/tomes) project.

It is written in Python.

Its purpose is to:

1. Create a "tagged" version of an [EAXS](http://www.history.ncdcr.gov/SHRAB/ar/emailpreservation/mail-account/mail-account_docs.html) file(s) - an XML schema for storing email account information.
2. Package the original EAXS file(s) and the tagged EAXS file(s) into an Archival Information Package.

The tagged version of the EAXS file is meant to contain email messages that have been tagged by Name Entity Recognition (NER) tools.

The information package contents will contain not only the EAXS file(s), but also a [METS](http://www.loc.gov/standards/mets/mets-home.html) file, message attachments, statistical information, and other relevant data.

...

**TOMES Tool**  is under active development by the [State Archives of North Carolina](http://archives.ncdcr.gov/) in conjunction with the [TOMES Project Team](https://www.ncdcr.gov/resources/records-management/tomes/team). Currently, it is not intended for use other than testing by the project team.


## Dependencies

TOMES Tool requires the following applications:

- [Python 3+](https://www.python.org/download/releases/3.0/) (using 3.6)
	- See the [../requirements.txt](https://github.com/StateArchivesOfNorthCarolina/tomes_tool/blob/master/requirements.txt) file for additional module dependencies.
- [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) 3.7+ (using 3.7.0)
	- *We're currently using this for NER tagging.*
	- Please see the CoreNLP documentation for Java and memory requirements, etc.
	- You **must** place the [regexner_TOMES](https://github.com/StateArchivesOfNorthCarolina/tomes_tool/tree/master/lib/stanford.edu/stanford-corenlp-full-2016-10-31) directory and its files into the CoreNLP directory that contains the master JAR file (~"stanford-corenlp-3.7.0.jar").
- [Lynx](http://lynx.browser.org/) 2.8.8+ (using 2.8.8)
	- *We're currently using this for HTML email to plain text conversion.*
	- The "lynx" command must be executable from any directory on your system.
		- For Windows, this will likely require editing your Environmental Variables "PATH" to include the path to the lynx.exe file.


## Quick Tests

You can run all the unit tests in the [../tests](https://github.com/StateArchivesOfNorthCarolina/tomes_tool/blob/master/tests/) directory: `py -3 -m unittest`

Specific unit tests of interest:

- `py -3 -m unittest test__html_to_text.py`
	- This primarily tests that Lynx can be called by TOMES Tool.
- `py -3 -m unittest test__eaxs_to_tagged.py`
	- This tests the EAXS to tagged EAXS workflow without actually calling CoreNLP or Lynx.

You can also test CoreNLP by starting it and going to the correct local URL, i.e. "localhost:9000". To save time, it is recommended to only enter *very* short text (e.g. "George Washington").


## Sample Files 

Sample files are located in the [../tests/sample_files](https://github.com/StateArchivesOfNorthCarolina/tomes_tool/blob/master/tests/sample_files/) directory.

The sample files can be used with the Python unit test scripts.

To test these scripts on sample files, simply call the scripts with the `-h` option: `py -3 test__[rest of filename].py -h` and try the example.


## Usage

1. Create an EAXS file via [DarcMailCLI](https://github.com/StateArchivesOfNorthCarolina/DarcMailCLI).
2. Start the CoreNLP server.
	- Until further notice, it is assumed you will run the server on port 9000 with a lengthy timeout:
	
		`cd stanford-corenlp-full-2016-10-31`

     	`java -mx2g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 50000`
3. From the [root TOMES Tool directory](https://github.com/StateArchivesOfNorthCarolina/tomes_tool/) do: `py -3 main.py -h` 
4. Pass in your EAXS filepath (including the filename) per the instructions.
5. Let us know what happens.

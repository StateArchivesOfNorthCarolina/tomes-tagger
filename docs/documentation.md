# Introduction

**TOMES Tool** is part of the [TOMES](https://www.ncdcr.gov/resources/records-management/tomes) project.

It is written in Python.

Its purpose is to:

1. Create a deliverable version of an [EAXS](http://www.history.ncdcr.gov/SHRAB/ar/emailpreservation/mail-account/mail-account_docs.html) file(s) - an XML schema for storing email account information.
2. Package the original EAXS file(s) and the deliverable EAXS file(s) into an Archival Information Package.

The deliverable version of the EAXS file is meant to contain email messages that have tagged by Name Entity Recognition (NER) tools to facilitate archival processing.

The information package contents will contain not only the EAXS file(s), but also a [METS](http://www.loc.gov/standards/mets/mets-home.html) file, message attachments, statistical information, and other relevant data.

...

**TOMES Tool**  is under active development by the [State Archives of North Carolina](http://archives.ncdcr.gov/) in conjunction with the [TOMES project team](https://www.ncdcr.gov/resources/records-management/tomes/team). As such, it it not currently intended for use other than testing by the project team.


## Dependencies

TOMES Tool requires the following applications:

- [Python 3+](https://www.python.org/download/releases/3.0/) (using: 3.6)
	- See the ../requirements.txt file for additional module dependencies.
- [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) 3.7+ (using: 3.7.0)
	- Please see the CoreNLP documentation for Java requirements, etc.
- [Lynx](http://lynx.browser.org/) 2.8+ (using 2.8.8)
	- The "lynx" command must be executable from any directory on your system.
	- For Windows, this will likely require editing your Environmental Variables "PATH" to include the path to the lynx.exe file.


## Quick Tests
- Run the following unit tests from the "tests" directory:
	- `py -3 -m unittest test__html_to_text.py`
		- This tests that Lynx can be called by TOMES Tool.
	- `py -3 -m unittest test__eaxs_to_tagged.py`
		- This tests the EAXS to "tagged" EAXS workflow without calling CoreNLP or Lynx.

You can also test CoreNLP by starting it and going to the correct local URL, i.e. "localhost:9000". It's recommended to only enter *very* short text (e.g. "George Washington") so as to save time.

## Sample Files
Some simple sample files are located in the "tests/sample_files/" directory for quick testing.

The Python unit test scripts in the "tests" directory also have command line options. To test these scripts on sample files, simply call the scripts without the `-m unittest` option. 


## Usage

1. Create an EAXS file via [DarcMailCLI](https://github.com/StateArchivesOfNorthCarolina/DarcMailCLI).
2. Start the CoreNLP server.
	- Until further notice, it is assumed you will run the server on port 9000 with a lengthy timeout a la:
	
		`cd stanford-corenlp-full-2016-10-31`

     	`java -mx2g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 50000`
3. Do: `py -3 main.py -h` from the root TOMES Tool directory.
4. Pass in your EAXS filepath per the instructions.
5. Let us know what happens.

	
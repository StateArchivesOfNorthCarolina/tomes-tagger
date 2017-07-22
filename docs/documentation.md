# Introduction

**TOMES Tool** is part of the [TOMES](https://www.ncdcr.gov/resources/records-management/tomes) project.

It is written in Python.

Its purpose is to:

1. Create a deliverable version of an [EAXS](http://www.history.ncdcr.gov/SHRAB/ar/emailpreservation/mail-account/mail-account_docs.html) file(s) - an XML schema for storing email account information.
2. Package the original EAXS file(s) and the deliverable EAXS file(s) into an Archival Information Package.

The deliverable version of the EAXS file is meant to contain email messages that have tagged by Name Entity Recognition (NER) tools to facilitate archival processing and eventually discovery.

The information package contents will contain not only the EAXS file(s), but also a [METS](http://www.loc.gov/standards/mets/mets-home.html) file, message attachments, statistical information, and other relevant data.

...

**TOMES Tool**  is under active development by the [State Archives of North Carolina](http://archives.ncdcr.gov/) in conjunction with the [TOMES project team](https://www.ncdcr.gov/resources/records-management/tomes/team). As such, it it not currently intended for use other than testing by the project team.

## Dependencies

TOMES Tools requires the following applications.

- [Python 3+](https://www.python.org/download/releases/3.0/) (using: 3.6)
	- See the ../requirements.txt file for additional module dependencies.
- [Stanford CoreNLP](https://stanfordnlp.github.io/CoreNLP/) 3.7+ (using: 3.7.0)
	- Please see the CoreNLP documentation for Java requirements, etc.
- [Lynx](http://lynx.browser.org/) 2.8+ (using 2.8.8)
	- The "lynx" command must be executable from any folder on your system.
	- For Windows, this will likely require editing you Environmental Variables "PATH" to include the path to the lynx.exe file.

## Usage:

- First, create an EAXS file via [DarcMailCLI](https://github.com/StateArchivesOfNorthCarolina/DarcMailCLI).
- Start the CoreNLP server.
	- Until further notice, it is assumed you will run the server on port 9000 with a lengthy timeout a la:

    	`cd stanford-corenlp-full-2016-10-31`

    	`java -mx2g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 50000`
- Then do: `py -3 main.py -h` from the root TOMES Tool folder.
- Pass in your EAXS file per the instructions.
- Let us know what happens.

	
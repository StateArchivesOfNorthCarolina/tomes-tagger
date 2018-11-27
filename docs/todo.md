# Ideas for Future Work

- Add a description about the difference between a "tagged" EAXS file and the original. This should probably go into a new Markdown file.
- Because of workflow decisions, the tagging process continues even if a message or messages cannot be tagged (due to not having Lynx, timeouts, etc.) but the information about skipped messages that are skipped is in the log files. This should probably be outputted to the event logger and any METS templates in the `TOMES Packager` repository should be adjusted so that this information is stored in the PREMIS event related to tagging.
- These three modules have a static method to remove control characters:	

	- `./tomes_tagger/lib.eaxs_to_tagged`
	- `./tomes_tagger/lib.nlp_to_xml`
	- `./tomes_tagger/lib.text_to_nlp`
	
	Consider centralizing this function into a standalone module.
- Both `./tomes_tagger/lib/eaxs_to_tagged.py` and `./tomes_tagger/lib/nlp_to_xml.py` declare the GitHub namespace URI for EAXS. Given that this URL might be volatile going forward, it might be better to establish this in `./tomes_tagger/tagger.py` and pass it down into those modules. This would also make it possible to pass a different URI via the command line.

- It's possible that we could see improvements by using a different library to wrap CoreNLP. But we will need to investigate how this changes error handling, etc. In other words, this may not be a trivial change.

- Given how long some EAXS files take to tag, it might be nice to have an optional "live reporter" option.

	The idea is to pass an optional script or function to tagger.py's main method AND an int. The int is the time (in minutes) at which the tagging process will run the script's function. If the int value is 60, for example, the tagging process will run the function when the tagging process starts, every hour, and finally when the tagging process completes. This would allow someone to pass in a script or function that reports on the current status (tagged messages/total messages) via Slack, email, etc. The script or function takes one position argument (string) which is the progress data to report.

	To avoid adding two arguments, the best way to pass the arguments in might be as a tuple, where the first item is the script path or function and the second item is the time interval.

	For those who only want notifaction when processing starts/stops, passing in "0" as the int should be the way to make that happen.

- Consider working on signature extraction and omitting signatures from NLP/NER recognition in favor of just tagging them as "signatures".

	For early tests, see `./scripts/experiments/signatures`.

	See also: [http://blog.humaneguitarist.org/2017/05/06/spotting-the-john-hancock-in-emails/](http://blog.humaneguitarist.org/2017/05/06/spotting-the-john-hancock-in-emails/).

- Consider using Python to process regular expressions instead of CoreNLP. CoreNLP's use of tokens makes it difficult to effectively translate regex patterns better suited for use over non-tokenized text.

	For early tests on how to integrate non-tokenized regex matches with NER tokens from CoreNLP, see `./scripts/experiments/tag_text_after_tokenization`.





# Ideas for Future Work

- These three modules have a static method to remove control characters:	

	- ./tomes_tool/lib.eaxs\_to\_tagged
	- ./tomes_tool/lib.nlp\_to\_xml
	- ./tomes_tool/lib.text\_to\_nlp
	
	Consider centralizing this into a standalone module and just importing the function.

- It's possible that we could see improvements by using a different library to wrap CoreNLP. But we will need to investigate how this changes error handling, etc. In other words, this may not be a trivial change.

- Given how long some EAXS files take to tag, it might be nice to have an optional "live reporter" option. The idea is to pass an optional script or function to tagger.py's main method AND an int. The int is the time (in minutes) at which the tagging process will run the script/function. If the int value is 60, for example, the tagging process will run the script/function when the tagging process starts, every hour, and finally when the tagging process completes. This would allow someone to pass in a script/function that reports on the current status (tagged messages/total messages) via Slack, email, etc. The script/function takes one position argument (string) which is the progress data to report.

	To avoid adding two arguments, the best way to pass the arguments in might be as a tuple, where the first item is the script path or function and the second item is the time interval.

	For those who only want notifaction when processing starts/stops, passing in "0" as the int should be the way to make that happen.

- Consider working on signature extraction and omitting signatures from NLP/NER recognition in favor of just tagging them as "signatures". See "./scripts/experiments/signatures".

- Consider using Python to process regular expressions instead of CoreNLP. See "./scripts/experiments/tag\_text\_after\_tokenization". *Note: this requires the same tokenizer as CoreNLP but does not require parts-of-speech tagging or NLP analysis, etc. as that will only add additional processing overhead.*






# ???
import codecs
import json
from pycorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP("http://localhost:9000")
text = "Good morning John!\n\nLove,\nMarsha"
output = nlp.annotate(text, properties={"annotators":"tokenize, ssplit, pos, ner, regexner", "outputFormat":"json", "regexner.mapping":"regexner_TOMES/mappings.txt"})
output = json.dumps(output, indent=2)
with codecs.open("sample_files/sample_NER.json", "w", encoding="utf-8") as f:
	f.write(output)

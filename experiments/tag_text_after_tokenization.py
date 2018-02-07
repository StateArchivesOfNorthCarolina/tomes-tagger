""" This tests a solution to:

    "If I use an NER tagger that tokenizes a given text, how can I use regular expressions 
    over the non-tokenized text and merge the results with the NER tagger results?"

    This would need to be refactored to remove redundancy, but each function is attempting
    to show logic rather than the most efficient way of passing the data around.
"""

def tokenize(text):
    """ This takes the place of the tokenizer or tokenization algorithm used by CoreNLP (or 
    some other NER tagger being used). It returns a list of tokens in @text. """

    tokens = text.split()
    return tokens


def lookup_tag(regex_pattern):
    """ For each @regex_pattern we need a dict so we can lookup the associated NER tag. """

    lookup = {"[H|h]ello world": "GREETING"}
    try:
        return lookup[regex_pattern]
    except KeyError:
        return None


def get_map(tokens):
    """ Returns a dictionary with each unique token in @tokens as keys. The values are lists:
    the index/s of the position in @tokens that the token is found. """

    token_index = enumerate(tokens)
    token_map = {}
    for k, v in token_index:
        if v in token_map.keys():
            token_map[v].append(k)
        else:
            token_map[v] = [k]

    return token_map


def get_combos(haystack, needle):
    """ @haystack is the text you are tokenizing/tagging and also running regexs over.
    @needle is the regex result obtained from running a regex over the text. """

    # ideally, these would be passed in rather than being computed here.
    haystack_tokens = tokenize(haystack)
    haystack_map = get_map(haystack_tokens)
    
    # we need this in order to find if/where it exists in @haystack_tokens as a subset.
    needle_tokens = tokenize(needle)

    # get position of first token in @needle_tokens (i.e. the tokenized regex 
    # results) and the total number of tokens in the regex results.
    try:
        finds = haystack_map[needle_tokens[0]]
        distance = len(needle_tokens)
    except KeyError:
        return None

    # make a list of tokens sets in @haystack_tokens that match @needle_tokens.
    combos = []
    for find in finds:
        combo = {"tokens": haystack_tokens[find:find + distance], "position": find}
        if combo["tokens"] == needle_tokens:
            combos.append(combo)

    return combos


# sample text and regex.
TEXT = "... Hello world ... hello world again!"
PATTERN = "[H|h]ello world"

# test functions.
print(tokenize(TEXT))
print(lookup_tag(PATTERN))
print(get_map(tokenize(TEXT)))
print(get_combos(TEXT, "Hello world"))
print()

# example usage.
import re

ner_tag = lookup_tag(PATTERN)
matches = re.findall(PATTERN, TEXT)
print("Found {} matches.".format(len(matches)))
for match in matches:
    results = get_combos(TEXT, match)
    for result in results:
        message = "Tagging each token in {} with '{}'".format(result, ner_tag)
        print(message)
        concatenated = " ".join(result["tokens"])
        message = "Concatenated tokens: {}".format(concatenated)
        print(message)
    

####['...', 'Hello', 'world', '...', 'hello', 'world', 'again!']
####GREETING
####{'...': [0, 3], 'Hello': [1], 'world': [2, 5], 'hello': [4], 'again!': [6]}
####[{'tokens': ['Hello', 'world'], 'position': 1}]
####
####Found 2 matches.
####Tagging each token in {'tokens': ['Hello', 'world'], 'position': 1} with 'GREETING'
####Concatenated tokens: Hello world
####Tagging each token in {'tokens': ['hello', 'world'], 'position': 4} with 'GREETING'
####Concatenated tokens: hello world

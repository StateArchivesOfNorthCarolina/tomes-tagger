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
    return lookup[regex_pattern]


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


def get_locations(haystack, needle):
    """ @haystack is the text you are tokenizing/tagging and also running regexs over.
    @needle is the regex result obtained from running a regex over the text. """

    # ideally, these would be passed in rather than being computed here.
    haystack_tokens = tokenize(haystack)
    haystack_map = get_map(haystack_tokens)
    needle_tokens = tokenize(needle)
    needle_map = get_map(needle_tokens)

    # get positions of first and last token in @needle_tokens (i.e. the tokenized regex 
    # results).
    try:
        first, last = haystack_map[needle_tokens[0]], haystack_map[needle_tokens[-1]]
    except KeyError:
        return None

    # make a list of tokens in @haystack_tokens that have the same first/last tokens as the
    # tokenized regex match (@needle_tokens).
    combos = []
    
    # only store results where the last haystack token's position is greater than the first 
    # token because otherwise we know the concatenated string won't match the regex result.
    for fir in first:
        for las in last:
            if las >= fir:
                combos.append((fir, las + 1))

    return combos


def locate(text, regex_result):
    """ This returns a list of each token to tag as well as the start/stop position of the 
    matching @regex_result inside a source @text. """
    
    try:
        locations = get_locations(text, regex_result)
    except TypeError:
        return []

    tokens = tokenize(text)
    regex_tokens = tokenize(regex_result)
        
    # see if the token span in @locations matches @regex_tokens.
    results = []
    for start, distance in locations:
        find = tokens[start:distance]
        if find == regex_tokens:
            result = find, start, distance
            results.append(result)

    return results


# sample text and regex.
TEXT = "... Hello world ..."
PATTERN = "[H|h]ello world"

# test functions.
##print(tokenize(TEXT))
##print(lookup_tag(PATTERN))
##print(get_map(tokenize(TEXT)))
##print(get_locations(TEXT, "Hello world"))

# example usage.
import re

regex_match = re.search(PATTERN, TEXT).group()
ner_tag = lookup_tag(PATTERN)
for result in locate(TEXT, regex_match):
    tokens, start, stop = [r for r in result]
    message = "Tagging each in {} with '{}'".format(tokens, ner_tag)
    print(message)
    concatenated = " ".join(tokenize(TEXT)[start:stop])
    print("Concatenated result: {}".format(concatenated))
    
##Tagging each in ['Hello', 'world'] with 'GREETING'
##Concatenated result: Hello world

# -*- coding: utf-8 -*-
from nltk.tokenize import sent_tokenize
from spacy.en import English
import re
from nltk.tag.stanford import StanfordNERTagger
import nltk as n_ltk


class SentenceSplit(object):
    NLTK_SPLITTER = 1
    SPACY_SPLITTER = 2
    STANFORD_SPLITTER = 3
    DEFAULT_FILTERS = ['^<{0,1}http.{0,1}:',
                       '^.{0,2}\n{2,4}',
                       '^.*@.*',
                       '^_+',
                       '^<mailto:']

    def __init__(self, tpe):

        self.content = None
        self.split_sents = []
        self.type = tpe

    def factory(self, msg):
        """
        @type msg Message.MessageBlock
        """
        if self.type == 1:
            return NltkSplitter(object)
        if self.type == 2:
            return SpacySplitter(object)
        if self.type == 3:
            return StanfordSplitter(object)


class NltkSplitter(SentenceSplit):

    def get_sentences(self, text):
        """
        @type text str
        @:rtype list[str]
        """
        for t in text:
            self.split_sents = sent_tokenize(t)
        return self.split_sents

    @staticmethod
    def filter(fltr_pkg, text):
        """
        @type text str
        @type fltr_pkg list[str]
        @:rtype list[str]
        """
        matched = False
        for reg in fltr_pkg:
            if re.match(reg, text):
                matched = True
                break
        return matched

    def locate_signature(self, tag_list):
        others = 0.00001
        tagged = 0.0
        lst = []
        token_sentence = n_ltk.word_tokenize(tag_list)
        tagged_sent = n_ltk.pos_tag(token_sentence)
        chunks = n_ltk.ne_chunk(tagged_sent)
        for t in chunks:
            if hasattr(t, 'label') and t.label:
                tagged += 1
                label = t.label
                word = t[0][0]
            else:
                others += 1
                label = 'O'
                word = t[0]
            lst.append((word, label))
        lst.append(tagged / others)
        return lst


class SpacySplitter(SentenceSplit):
    print("Loading Spacy English Model...")
    nlp = English()

    def get_sentences(self, text):
        """
        @type text str
        @:rtype list[spacy.tokens.doc.Doc]
        """

        for t in text:
            doc = self.nlp(u'%s' % t)
            for s in doc.sents:
                self.split_sents.append(s)
        return self.split_sents

    @staticmethod
    def filter(fltr_pkg, text):
        """
        @type text spacy.tokens.doc.Doc
        @type fltr_pkg list[str]
        @:rtype list[str]
        """
        matched = False
        for reg in fltr_pkg:
            if re.match(reg, text.text):
                matched = True
                break
        return matched

    @staticmethod
    def locate_signature(tag_list):
        others = 0.00001
        tagged = 0.0
        lst = []
        for token in tag_list:
            if re.match('^\n', token.text):
                continue
            if token.ent_iob_ != "O":
                tpe = token.ent_type_
                tagged += 1
            else:
                tpe = 'O'
                others += 1
            lst.append((token.text, tpe))
        lst.append(tagged / others)
        return lst


class StanfordSplitter(SentenceSplit):
    tagger = StanfordNERTagger(
        '.\stanford\english.all.3class.distsim.crf.ser.gz',
        '.\stanford\stanford-ner.jar')

    def get_sentences(self, text):
        """
        @type text str
        @:rtype list[str]
        """
        for t in text:
            self.split_sents = sent_tokenize(t)
        return self.split_sents

    @staticmethod
    def filter(fltr_pkg, text):
        """
        @type text str
        @type fltr_pkg list[str]
        @:rtype list[str]
        """
        matched = False
        for reg in fltr_pkg:
            if re.match(reg, text):
                matched = True
                break
        return matched

    @staticmethod
    def locate_signature(self, tag_list):
        others = 0.00001
        tagged = 0.0
        lst = []
        tags = self.tagger.tag(tag_list.split())
        for word, iob in tags:
            if re.match('^\n', word):
                continue
            if iob != "O":
                tagged += 1
            else:
                others += 1
            lst.append((word, iob))
        lst.append(tagged / others)
        return lst


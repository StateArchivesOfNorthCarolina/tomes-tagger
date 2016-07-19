from SentenceSplit import SentenceSplit as SS


class ContentCleaner:
    def __init__(self, messages):
        """
            @type messages list[Message.MessageBlock]
        """
        self.msgs = messages
        self.tags = []
        self.cleaned_sentences = []
        self.content = None
        self.from_email = None

    def clean_message(self):
        pass

    def set_message_ratios(self):
        ratios = []
        for message in self.msgs:
            try:
                if message.ret_path:
                    # If there is no from_email this is most likely not email or it is a draft email
                    if message.content or len(message.content) > 0:
                        sentence = SS(SS.STANFORD_SPLITTER)
                        splitter = sentence.factory(message)
                        splitter.get_sentences(message.content)
                        for sent in splitter.split_sents:
                            print ("Classifying a sentence from: %s" % message.from_id)
                            ratio = splitter.locate_signature(sent)
                            rat_pop = ratio.pop()
                            ratios.append(rat_pop)
                            message.set_sentence_vector(sent.text, rat_pop)
            except AttributeError as e:
                self. tags = ()
            except IndexError:
                self.tags = ()

    def clean_for_training(self):
        ratios = []
        for message in self.msgs:
            try:
                if message.ret_path:
                    # If there is no from_email this is most likely not email or it is a draft email
                    if message.content or len(message.content) > 0:
                        sentence = SS(SS.SPACY_SPLITTER)
                        splitter = sentence.factory(message)
                        splitter.get_sentences(message.content)
                        for sent in splitter.split_sents:
                            if splitter.filter(splitter.DEFAULT_FILTERS, sent):
                                continue
                            ratio = splitter.locate_signature(sent)
                            rat_pop = ratio.pop()
                            ratios.append(rat_pop)
                            if rat_pop > .30:
                                pass
                            else:
                                self.cleaned_sentences.append(ratio)
                            message.set_sentence_vector(sent, rat_pop)
            except AttributeError as e:
                print e
                self. tags = ()
            except IndexError:
                self.tags = ()
            print(ratios)
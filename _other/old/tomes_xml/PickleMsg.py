import cPickle as pkl
import gzip


class TomesPickleMsg:
    default_loc = "./messages.pkl"

    def __init__(self, msgs=None):
        """
        @type msgs list[Message.MessageBlock]
        """
        self.unpickled_messages = msgs
        self.pkl_package = None

    def serialize(self, msgs=None, location=default_loc):
        """
         @type location str
        """
        if msgs:
            self.unpickled_messages = msgs
        f = gzip.GzipFile(location, 'wb')
        pkl.dump(self.unpickled_messages, f, -1)
        self.unpickled_messages = None
        f.close()

    def deserialize(self, location=default_loc):
        """
        @:rtype list[Message.MessageBlock]
        @type location str
        """
        f = gzip.GzipFile(location, 'rb')
        obj = pkl.load(f)
        f.close()
        return obj

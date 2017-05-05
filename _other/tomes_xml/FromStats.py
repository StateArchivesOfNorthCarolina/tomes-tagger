import numpy as np


class FromStat:

    def __init__(self):
        """
        @type message_map dict
        @type message_container list
        """
        self.message_map = {}
        self.message_container = []

    def set_message_shape(self, tup, id):
        """
        @type tup tuple
        @type id str
        """
        if len(tup) == 0:
            return
        if id in self.message_map:
            self.message_container = self.message_map[id]
            self.message_container.extend(list(tup))
        else:
            self.message_container = []
            self.message_container.extend(list(tup))
            self.message_map[id] = self.message_container

    def get_from_contours(self, id):
        """
        @rtype list(float)
        """
        return self.message_map.get(id)

    def get_unique_occurrences(self, id):
        a = np.array(self.message_map.get(id))
        np.sort(a)
        unique, counts = np.unique(a, return_counts=True)
        return dict(zip(unique, counts))

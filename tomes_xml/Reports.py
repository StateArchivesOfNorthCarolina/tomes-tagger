from tomes_xml.PickleMsg import TomesPickleMsg as tpm


class StatPackages:
    def __init__(self, msg_list, from_stats):
        """
        :param list[Message.MessageBlock] msg_list:
        :param FromStats.FromStat from_stats:
        """
        self.msgs = msg_list
        self.from_stats = from_stats
        self.report()

    def report(self):
        # Get list of IDS
        """
        @type list[Message.MessageBlock] m_group
        :return:
        """
        for key in self.from_stats.message_map.iterkeys():
            uo = self.from_stats.get_unique_occurrences(key)
            m_group = self.get_msgs_by_from(key)
            for m in m_group:
                for a, b in m.sentence_vectors:
                    if b == 0.0:
                        continue
                    if b < 1.5:
                        continue
                    if b > 10:
                        continue
                    if b in uo:
                        print a
                        print ('________\n')

    def get_msgs_by_from(self, id):
        """
        :param str id:
        :return list[Message.MessageBlock]:
        """
        lst = []
        for m in self.msgs:
            if m.from_id == id:
                lst.append(m)
        return lst


if __name__ == "__main__":
    tpmi = tpm()
    stat_p = StatPackages(tpmi.deserialize(), tpmi.deserialize('from_stats.pkl'))
    print
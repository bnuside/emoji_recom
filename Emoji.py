import re


class EmojiChar(object):
    def __init__(self):
        with open('emoji_code', 'r') as ef:
            self._emojis = ef.read().splitlines()

        self._emoji_pat = None
        self._non_en_emoji_pat = None
        self._unknown_pat = None
        self._split_pat = None

    @property
    def emoji_pat(self):
        return re.compile(u'+|'.join(self._emojis))

    @property
    def non_en_emoji_pat(self):
        pat_str = u'[^\w\.\?\'\"!\d\^\&\*\(\)\|{}\[\]:|%s]+' % '|'.join(self._emojis)
        return re.compile(pat_str)

    @property
    def unknown_pat(self):
        return re.compile(u'['u'\U000000A0-\U000022FF'u'\U00002400-\U000025FF'u'\U00002C00-\U0001F000]+')

    @property
    def split_pat(self):
        pat_str = u'[\s\.\!\?\(\),\*\":]+|([%s]+)' % '|'.join(self._emojis)
        return re.compile(pat_str)

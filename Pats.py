import re

BOUNDARIES = '[\s\?\.\!,;:<>\[\]\{\}\-\+\=\(\)\*\d@#\$\^\&\n]'
NON_SINGLE_ALPHA = '^[^a-zA-Z]+$'
SINGLE_WORD = r'^%s*\b\w+\b%s*$' % (BOUNDARIES, BOUNDARIES)
UKNOWN = u'['u'\U000000A0-\U000022FF'u'\U00002400-\U000025FF'u'\U00002C00-\U0001F000]+'

with open('emoji_code', 'r') as ef:
    _emojis = ef.read().splitlines()

_easy_emoji_pat = re.compile('['u'\U00002300-\U000023FF'u'\U00002600-\U000026FF'  # Miscellaneous Symbols
                             u'\U0001F600-\U0001F64F'  # emoticons
                             u'\U0001F300-\U0001F5FF'  # symbols & pictographs
                             u'\U0001F680-\U0001F6FF'  # transport & map symbols
                             u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                             ']', flags=re.UNICODE)


def get_easy_emoji_split():
    epat = re.compile('(['u'\U00002300-\U000023FF'u'\U00002600-\U000026FF'  # Miscellaneous Symbols
                      u'\U0001F600-\U0001F64F'  # emoticons
                      u'\U0001F300-\U0001F5FF'  # symbols & pictographs
                      u'\U0001F680-\U0001F6FF'  # transport & map symbols
                      u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                      ']{1})', flags=re.UNICODE)
    return epat


def get_word_split():
    return re.compile(r'[\s\.\?\!\@\[\]\{\}\|\(\)\d\*\+=]+')


def get_emoji_pat(easy=False):
    if easy:
        return _easy_emoji_pat
    return re.compile(u'+|'.join(_emojis))


def non_en_emoji_pat():
    pat_str = u'[^\w\.\?\'\"!\d\^\&\*\(\)\|{}\[\]:|%s]+' % '|'.join(_emojis)
    return re.compile(pat_str)


def get_unknown_pat():
    boundaries = '[\s\?\.\!,;:<>\[\]\{\}\-\+\=\(\)\*\d@#\$\^\&]'
    pat_unk1 = re.compile(r'(?<=%s)[^\s]{15,}(?=\b%s*)'
                          r'|(?<=%s)\d+[\$]*(?=\b%s*)'
                          r'|(?<=%s)[\d:/\-]+(?=\b%s*)'
                          r'|(?<=%s)(?P<dup>\w)(?P=dup){3,}(?=\b%s*)' % (
                          boundaries, boundaries, boundaries, boundaries, boundaries, boundaries, boundaries,
                          boundaries))
    pat_unk2 = re.compile(
        u'(?<=%s)['u'\U000000A0-\U000022FF'u'\U00002400-\U000025FF'u'\U00002C00-\U0001F000]+(?=\b%s*)' % (
        boundaries, boundaries))

    # return re.compile(u'['u'\U000000A0-\U000022FF'u'\U00002400-\U000025FF'u'\U00002C00-\U0001F000]+')
    return pat_unk1, pat_unk2


def get_emojicode_list():
    return _emojis


def get_punc_pat():
    pun_margin = '(?<=\w)[\?\.\!,;:\[\]\{\}\-\+\=\(\)\*\d@#\$\^\&\]\s]+(?=\w*)'
    pat_pun = re.compile(pun_margin)
    return pat_pun

import collections
import re
import os
import time

full_path = '/Users/side/Downloads/emoji_sample.txt'
sample_path = '/Users/side/Downloads/emoji_sample_head.txt'
st_path = 'sampletest.txt'

process_path = full_path

emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]{1}?", flags=re.UNICODE)
emoji_pattern2 = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)

non_emoji_pattern = re.compile(
    # '[^a-zA-Z0-9]'
    '[^\w\.\'"\-\?!,\\/\$\^\{\[\(\|\)\*\+>=&%#@]{1}?'
    # '[^\w@]{1}?'
)

def clean_data():
    start_t = time.time()
    with open(process_path, 'r+') as f:
        content = f.read()
        make_log('finding all emojis')
        all_emoji = re.findall(non_emoji_pattern, content)

        make_log('distincting emojis')
        distincted_emoji = set(all_emoji)
        # print(all_emoji)
        # print(distincted_emoji)

        make_log('replacing emoji')
        for emoji in distincted_emoji:
            content = content.replace(emoji, ' %s ' % emoji)

        make_log('writing file')
        f.seek(0, os.SEEK_SET)
        f.write(content)
    end_t = time.time()
    spend = end_t - start_t
    make_log(spend)

def word_freq():
    full_path = '/Users/side/Downloads/emoji_sample.txt'
    sample_path = '/Users/side/Downloads/emoji_sample_head.txt'
    st_path = 'sampletest.txt'

    with open(process_path, 'r') as f:
        content = f.read()

        make_log('replace enter and split')
        word_list = re.split('\s+', content.replace('\n', ' <eos> '))
        make_log('wordlist length: %d' % len(word_list))
        counter = collections.Counter(word_list)
        st = time.time()
        make_log('sorting pairs')
        counter_pairs = sorted(counter.items(), key = lambda x: (-x[1], x[0]))
        et = time.time()
        make_log(et-st)
        words, _ = list(zip(*counter_pairs))
        make_log('length before filter: %d' % len(words))

        words = list(filter(limit_filter, words))
        make_log(type(words))
        make_log('length after filter: %d' % len(words))
        make_log('writing word file: words.txt')
        with open('words.txt', 'w') as wf:
            wf.writelines('\n'.join(words))

        pass

def check_sample():
    emoji_pattern = re.compile(".*["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "].*", flags=re.UNICODE)
    emoji_pattern2 = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)

    full_path = '/Users/side/Downloads/emoji_sample.txt'
    with open(full_path, 'r') as f:
        ret = f.readlines(10240)
        for l in ret:
            mat = emoji_pattern.match(l)
            if mat:
                make_log(l)

def test_writelines():
    l = ['one', 'two', 'three']
    with open('test.txt', 'w')as tf:
        tf.writelines('\n'.join(l))

def test_emoji():
    pat = re.compile('\W{1}?')
    non_char = []
    # with open(st_path, 'r') as f:
    #     non_char = re.findall(non_emoji_pattern, f.read())
    #     make_log(set(non_char))
    s = 'hi i #$%^&*(!'
    non_char = re.findall(non_emoji_pattern, s)
    print(non_char)

def make_log(m):
    print('%s -> %s' % (time.asctime(time.localtime(time.time())), str(m)))

def limit_filter(word):
    pat = re.compile(r'^[!@#$%^&*().?\'"/\[]{}|=+-_$')
    return len(word) < 20 and not pat.match(word)

if __name__ == '__main__':
    clean_data()
    word_freq()
    # check_sample()
    # test_writelines()
    # test_emoji()
import collections
import re
import os
import time
import threading

full_orignal_path = 'emoji_sample.txt'
sample_orignal_path = 'emoji_sample_head.txt'
st_path = 'sampletest.txt'
full_processed_path = 'emoji_sample_processed.txt'
sample_process_path = 'emoji_sample_head_process.txt'
train_path = './data/emoji.train.txt'
valid_path = './data/emoji.valid.txt'
test_path = './data/emoji.test.txt'

logfile = open('process_log.txt', 'a')

emoji_pattern = re.compile("[" u"\U00002300-\U000023FF"u"\U00002600-\U000026FF"  # Miscellaneous Symbols
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]{1}?", flags=re.UNICODE)


unknown_pattern = re.compile(u'['u'\U000000A0-\U000022FF'u'\U00002400-\U000025FF'u'\U00002C00-\U0001F000]+')

def clean_data(content, finalpath):
    start_t = time.time()

    emojis = find_all_emojis(content)
    unknowns, puncwords = find_all_unknowns_and_puncwords(content)

    make_log('replacing emoji')
    for emoji in emojis:
        content = content.replace(emoji, ' %s ' % emoji)
    make_log('emoji replacement spent time: %ds' % (time.time() - start_t))

    make_log('replacing unknown')
    for unk in unknowns:
        content = content.replace(unk, ' <unk> ')
    make_log('unknowns replacement spent time: %ds' % (time.time() - start_t))

    make_log('replacing puncword')
    for k in puncwords.keys():
        for word in puncwords[k]:
            content = content.replace(word, k)
    make_log('puncword replacement spent time: %ds' % (time.time() - start_t))

    fw = open(finalpath, 'w')
    make_log('writing file')
    fw.write(content)
    fw.flush()
    fw.close()
    end_t = time.time()
    spend = end_t - start_t
    make_log(spend)

def word_freq(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        make_log('replacing all enter')
        content.replace('\n', ' <eos> ')

        word_list = re.split('[\s\.\!\?\(\),\*\":]+', content.lower())

        make_log('wordlist length: %d' % len(word_list))
        counter = collections.Counter(word_list)
        st = time.time()
        make_log('sorting pairs')
        counter_pairs = sorted(counter.items(), key = lambda x: (-x[1], x[0]))
        et = time.time()
        make_log(et-st)
        words, _ = list(zip(*counter_pairs))
        make_log('length before filter: %d' % len(words))

        # words = list(filter(limit_filter, words))[:10000]
        make_log('length after filter: %d' % len(words))
        make_log('writing word file: words.txt')
        with open('words.txt', 'w') as wf:
            wf.writelines('\n'.join(words))

def find_all_emojis(content):
    make_log('finding all emojis')
    all_emoji = re.findall(emoji_pattern, content)
    make_log('distincting emojis')
    return set(all_emoji)


def find_all_unknowns_and_puncwords(content):
    pat_other = re.compile('[\!@#\$%\^&\*\(\)\.\?"/\\\[\]{}\|=\+\-_\$;:,]+|^\d+[\$%]*$|^[\d:/\-]+$')
    pat_pun = re.compile('[\!@#\$%\^&\*\(\)\.\?"/\\\[\]{}\|=\+\-_\$;:,\d]+$')
    pat_dupword = re.compile('.*(?P<dup>\w)(?P=dup){3,}.*')

    make_log('finding all unknowns')
    word_list = re.split('[\s\.\?\!\,\(\)\"\;]+', content)
    ulist = []
    pdict = {}
    for word in word_list:
        if len(word) > 20:
            ulist.append(word)
            continue

        mat = unknown_pattern.match(word)
        if mat:
            ulist.append(word)
            continue

        mat = pat_other.match(word)
        if mat:
            ulist.append(word)
            continue

        mat = pat_dupword.match(word)
        if mat:
            ulist.append(word)

        mat = re.search(pat_pun, word)
        if mat:
            k = word[:mat.start()]
            if k not in pdict.keys():
                pdict.setdefault(k, [])
            pdict[k].append(word)

    ulist = set(ulist)
    return ulist, pdict


def make_log(m):
    global logfile
    fm = '%s -> %s' % (time.asctime(time.localtime(time.time())), str(m))
    logfile.write(fm)
    logfile.write('\n')
    logfile.flush()
    # print(fm)

def limit_filter(word):
    pat = re.compile('[\!@#\$%\^&\*\(\)\.\?\'"/\\\[\]{}\|=\+\-_\$;:]+')
    mat = pat.match(word)
    return len(word) < 20 and not mat


def get_test_and_valid_data():
    with open('emoji_sample.txt', 'r') as ef:
        lines = ef.readlines()
        valid_content = lines[10001:20000]
        test_content = lines[20001:30000]

        clean_data('\n'.join(valid_content), valid_path)
        clean_data('\n'.join(test_content), test_path)

if __name__ == '__main__':
    with open(sample_orignal_path, 'r') as sop:
        clean_data(sop.read(), train_path)
        word_freq(train_path)
    get_test_and_valid_data()
    logfile.close()
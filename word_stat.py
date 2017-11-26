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

logfile = open('process_log.txt', 'a')

emoji_pattern = re.compile("[" u"\U00002300-\U000023FF"u"\U00002600-\U000026FF"  # Miscellaneous Symbols
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]{1}?", flags=re.UNICODE)


unknown_pattern = re.compile(u'['u'\U000000A0-\U000022FF'u'\U00002400-\U000025FF'u'\U00002C00-\U0001F000]+')

def clean_data():
    start_t = time.time()

    fr = open(full_orignal_path, 'r')
    # content = fr.read(1*1024*1024)
    content = fr.read()
    fr.close()
    make_log('finding all emojis')
    all_emoji = re.findall(emoji_pattern, content)
    make_log('distincting emojis')
    distincted_emoji = set(all_emoji)


    make_log('replacing all enter')
    content.replace('\n', ' <eos> ')
    make_log('enter replacement spent time: %ds' % (time.time() - start_t))
    # print(all_emoji)
    # print(distincted_emoji)

    make_log('replacing emoji')
    for emoji in distincted_emoji:
        content = content.replace(emoji, ' %s ' % emoji)
    make_log('emoji replacement spent time: %ds' % (time.time() - start_t))

    fw = open(full_processed_path, 'w')
    make_log('writing file')
    fw.write(content)
    fw.flush()
    fw.close()
    end_t = time.time()
    spend = end_t - start_t
    make_log(spend)

def word_freq():
    with open(full_processed_path, 'r') as f:
        content = f.read()
        word_list = re.split('[\s\.\!\?\(\),\*\":]+', content)

        make_log('replacing unknown')
        st = time.time()
        make_unknown(word_list)
        make_log('replacing unknown spent %ds' % int(time.time() - st))

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
        make_log('length after filter: %d' % len(words))
        make_log('writing word file: words.txt')
        with open('words.txt', 'w') as wf:
            wf.writelines('\n'.join(words))

def make_unknown(content):
    pat = re.compile('[\!@#\$%\^&\*\(\)\.\?\'"/\\\[\]{}\|=\+\-_\$;:,]+|^\d+[\$%]*$|^\w{1}?$')
    pat_pun = re.compile('[\!@#\$%\^&\*\(\)\.\?\'"/\\\[\]{}\|=\+\-_\$;:,]+$')
    for index in range(len(content)):
        if len(content[index]) > 20:
            content[index] = '<unk>'
            continue
        mat = unknown_pattern.match(content[index])
        if mat:
            content[index] = '<unk>'
            continue
        mat = pat.match(content[index])
        if mat:
            content[index] = '<unk>'
            continue

        mat = re.search(pat_pun, content[index])
        if mat:
            content[index] = content[index][:mat.start()]
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


if __name__ == '__main__':
    clean_data()
    word_freq()
    logfile.close()
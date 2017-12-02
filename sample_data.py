import collections
import re
import os
import time
import random
from Emoji import EmojiChar

raw_sample_path = 'emoji_sample.txt'
logfile = open('process_log.txt', 'a')


def _bad_line(content, **kwargs):
    non_single_alphabet_pat = re.compile('^[^a-zA-Z]+$')
    margin = '[\s\?\.\!,;:<>\[\]\{\}\-\+\=\(\)\*\d@#\$\^\&\n]'
    single_word_pat = re.compile(r'^%s*\b\w+\b%s*$' % (margin, margin))

    lines = content.splitlines(True)
    ind = 0
    print('before delete length: %d' % len(lines))
    for line in lines:
        if len(line) < 5:
            lines[ind] = ''
            ind += 1
            continue
        mat1 = non_single_alphabet_pat.match(line)
        mat2 = kwargs['emoji_char'].unknown_pat.match(line)
        mat3 = single_word_pat.match(line)
        if mat1 or mat2 or mat3:
            lines[ind] = ''
        ind += 1
    return ''.join(lines)


def split_data(filepath, content):
    train_path = os.path.join(filepath, 'emoji.train.txt')
    valid_path = os.path.join(filepath, 'emoji.valid.txt')
    test_path = os.path.join(filepath, 'emoji.test.txt')

    # write train data
    lines = content.splitlines(True)
    total_len = len(lines)
    train_begin = random.randrange(1, total_len // 2)
    train_end = train_begin + total_len // 2
    with open(train_path, 'w') as train_file:
        train_file.writelines(lines[train_begin:train_end])

    valid_begin = random.randrange(0, train_begin)
    valid_end = valid_begin + total_len // 4

    # print('total length %d' % total_len)
    # print('train begin %d' % train_begin)
    # print('train end %d' % train_end)
    # print('valid begin %d' % valid_begin)
    # print('valid end %d' % valid_end)
    # print('half %d' % (total_len // 2))
    # print('qual %d' % (total_len // 4))

    if valid_end < train_begin:
        with open(valid_path, 'w') as valid_file:
            valid_file.writelines(lines[valid_begin:valid_end])
        with open(test_path, 'w') as test_file:
            test_file.writelines(lines[:valid_begin])
            test_file.writelines(lines[valid_end:train_begin])
            test_file.writelines(lines[train_end:])

    else:
        with open(valid_path, 'w') as valid_file:
            valid_file.writelines(lines[valid_begin:train_begin])
            valid_file.writelines(lines[train_end:(valid_end + train_end - train_begin)])
        with open(test_path, 'w') as test_file:
            test_file.writelines(lines[:valid_begin])
            test_file.writelines(lines[(valid_end + train_end - train_begin):])


def emoji_line(content):
    ec = EmojiChar()
    lines = content.splitlines()
    emoji_lines = []
    for line in lines:
        if re.search(ec.emoji_pat, line):
            emoji_lines.append(line)

    return '\n'.join(emoji_lines)


def clean_data(filepath, emoji_only=False):
    start_t = time.time()
    ec = EmojiChar()
    karg = {'emoji_char': ec}

    with open(raw_sample_path, 'r') as fr:
        content = fr.read()

    content = _bad_line(content, **karg)

    if emoji_only:
        content = emoji_line(content)

    unknowns, puncwords = find_all_unknowns_and_puncwords(content, **karg)

    make_log('replacing unknown')
    for unk in unknowns:
        content = content.replace(unk, '<unk>')
    make_log('unknowns replacement spent time: %ds' % (time.time() - start_t))

    make_log('replacing puncword')
    for k in puncwords.keys():
        for word in puncwords[k]:
            content = content.replace(word, k)
    make_log('puncword replacement spent time: %ds' % (time.time() - start_t))

    split_data(filepath, content)
    spend = time.time() - start_t
    make_log(spend)


def find_all_unknowns_and_puncwords(content, **kwargs):
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

        mat = kwargs['emoji_char'].unknown_pat.match(word)
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


if __name__ == '__main__':
    clean_data('./data/', emoji_only=True)
    logfile.close()

import collections
import re
import os
import time
import random
import Pats

raw_sample_path = 'emoji_sample.txt'


def exeTime(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        print("@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__))
        back = func(*args, **args2)
        print("@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__))
        print("%.3fs taken for {%s}" % (time.time() - t0, func.__name__))
        return back

    return newFunc


@exeTime
def _bad_line(content):
    non_single_alphabet_pat = re.compile(Pats.NON_SINGLE_ALPHA)
    margin = Pats.BOUNDARIES
    single_word_pat = re.compile(Pats.SINGLE_WORD)

    lines = content.splitlines(True)
    ind = 0
    print('before delete length: %d' % len(lines))
    for line in lines:
        if len(line) < 5:
            lines[ind] = ''
            ind += 1
            continue
        mat1 = non_single_alphabet_pat.match(line)
        mat2 = Pats.get_unknown_pat()[1].match(line)
        mat3 = single_word_pat.match(line)
        if mat1 or mat2 or mat3:
            lines[ind] = ''
        ind += 1
    return ''.join(lines)


@exeTime
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


@exeTime
def emoji_line(content):
    lines = content.splitlines()
    emoji_lines = []
    for line in lines:
        if re.search(Pats.get_emoji_pat(easy=True), line):
            emoji_lines.append(line)

    return '\n'.join(emoji_lines)


@exeTime
def clean_data(filepath, emoji_only=False):
    with open(raw_sample_path, 'r') as fr:
        content = fr.read().lower()

    content = _bad_line(content)
    if emoji_only:
        content = emoji_line(content)
    content = replace_pun_to_space(content)
    content = replace_tripdup_word(content)
    content = replace_unknown(content)

    split_data(filepath, content)


@exeTime
def clean_test_data(filepath, test_raw_path, emoji_only=False):
    with open(test_raw_path, 'r') as fr:
        content = fr.read().lower()

    content = _bad_line(content)
    if emoji_only:
        content = emoji_line(content)

    content = replace_pun_to_space(content)
    content = replace_tripdup_word(content)
    content = replace_unknown(content)

    with open('%s/emoji.test.txt' % filepath, 'w') as fw:
        fw.write(content)


@exeTime
def replace_unknown(content):
    pat_unk1, pat_unk2 = Pats.get_unknown_pat()

    content = pat_unk1.sub('<unk>', content)
    content = pat_unk2.sub('<unk>', content)
    content = Pats.get_punc_pat().sub(' ', content)
    return content


@exeTime
def replace_pun_to_space(content):
    pat = Pats.get_punc_pat()
    content = pat.sub(' ', content)
    return content


@exeTime
def replace_tripdup_word2(content):
    pat_dup = re.compile(r'(?P<dup>[a-zA-Z_])(\1{2,})')
    dup = re.search(pat_dup, content, flags=0)
    while dup:
        content = content[:dup.start() + 1] + content[dup.end():]
        dup = re.search(pat_dup, content, flags=0)

    return content


@exeTime
def replace_tripdup_word(content):
    pat_dup = re.compile(r'(?P<dup>[a-zA-Z_])(\1{2,})')

    lines = content.splitlines()
    for ind, line in enumerate(lines):
        # print(line, ind)
        dup = re.search(pat_dup, line, flags=0)
        while dup:
            lines[ind] = line[:dup.start() + 1] + line[dup.end():]
            line = line[:dup.start() + 1] + line[dup.end():]
            dup = re.search(pat_dup, line, flags=0)

    content = '\n'.join(lines)
    return content


@exeTime
def replace_suoxie(content):
    sub_pair = {'u': ' you ',
                'b': ' be ',
                'r': ' are ',
                'ur': ' your ',
                'im': ' i\'m ',
                'didnt': ' didn\'t ',
                'doesnt': ' doesn\'t ',
                'dont': ' don\'t ',
                'wont': ' won\'t ',
                'cant': ' can\'t ',
                'aint': ' ain\'t ',
                'couldnt': ' couldn\'t ',
                'wouldnt': ' wouldn\'t ',
                'fuckin': ' fucking ',
                'thx': ' thanks ',
                'plz': ' please ',
                }
    for key, value in sub_pair.items():
        pat = re.compile(r'\s%s\s|^%s\s|\s%s$' % (key, key, key))
        # content = content.replace(key, value)
        content = pat.sub(value, content)
    return content


@exeTime
def non_alphabet_emoji():
    pat = re.compile('[^'u'\U00002300-\U000023FF'u'\U00002600-\U000026FF'  # Miscellaneous Symbols
                             u'\U0001F600-\U0001F64F'  # emoticons
                             u'\U0001F300-\U0001F5FF'  # symbols & pictographs
                             u'\U0001F680-\U0001F6FF'  # transport & map symbols
                             u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                             'a-zA-Z\'\s\-]', flags=re.UNICODE)
    with open('emoji_sample_head.txt', 'r') as fr:
        content = fr.read().lower()

    content = pat.sub(' ', content)
    content = re.sub('\s{2,}', ' ', content)
    content = replace_tripdup_word(content)
    content = replace_suoxie(content)
    content = _bad_line(content)

    with open('temp.txt', 'w') as fw:
        fw.write(content)

if __name__ == '__main__':
    # clean_data('./data/', emoji_only=False)
    # replace_tripdup_word('')
    non_alphabet_emoji()
    s = 'i tell u this. u dont know u\nr'
    print(replace_suoxie(s))
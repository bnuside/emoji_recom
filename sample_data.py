import collections
import re
import os
import time
import random
import Pats

raw_sample_path = 'emoji_sample.txt'
logfile = open('process_log.txt', 'a')


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
    start_t = time.time()

    with open(raw_sample_path, 'r') as fr:
        content = fr.read(1024*1024).lower()

    content = _bad_line(content)
    if emoji_only:
        content = emoji_line(content)

    content = replace_tripdup_word(content)

    content = replace_unknown(content)

    split_data(filepath, content)
    spend = time.time() - start_t
    make_log(spend)


@exeTime
def replace_unknown(content):
    pat_unk1, pat_unk2 = Pats.get_unknown_pat()

    content = pat_unk1.sub('<unk>', content)
    content = pat_unk2.sub('<unk>', content)
    content = Pats.get_punc_pat().sub(' ', content)
    return content


@exeTime
def replace_tripdup_word(content):
    pat_dup = re.compile(r'(?P<dup>[a-zA-Z_])(\1{2,})')
    dup = re.search(pat_dup, content, flags=0)
    while dup:
        content = content[:dup.start()+1] + content[dup.end():]
        dup = re.search(pat_dup, content, flags=0)

    return content


def make_log(m):
    global logfile
    fm = '%s -> %s' % (time.asctime(time.localtime(time.time())), str(m))
    logfile.write(fm)
    logfile.write('\n')
    logfile.flush()
    # print(fm)


def test_rp_un():
    pass


if __name__ == '__main__':
    clean_data('./data/', emoji_only=False)
    # replace_tripdup_word('')
    logfile.close()

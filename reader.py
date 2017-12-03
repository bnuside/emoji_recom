from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os
import sys
import re
import Pats

import tensorflow as tf

Py3 = sys.version_info[0] == 3


def _read_words(filename):
    parts = _read_emojis(filename)
    ret = []
    for part in parts:
        if len(part) < 1:
            continue

        temp = re.split(Pats.get_word_split(), part)
        for word in temp:
            if len(word) < 1:
                continue
            ret.append(word)

    return ret


def _read_emojis(filename):
    with tf.gfile.GFile(filename, 'r') as f:
        if Py3:
            content = re.sub('\n', ' <eos> ', f.read())
        else:
            content = re.sub('\n', ' <eos> ', f.read().decode('utf-8'))

        return re.split(Pats.get_easy_emoji_split(), content)


def _build_vocab(filename, vocab_size):
    data = _read_words(filename)

    counter = collections.Counter(data)
    count_pairs = sorted(counter.items(), key=lambda x: (-x[1], x[0]))

    words, _ = list(zip(*count_pairs))
    word_to_id = dict(zip(words, range(vocab_size)))

    # 将单词转换成id，词频高的单词，id小
    return word_to_id


def _file_to_word_ids(filename, word_to_id):
    data = _read_words(filename)

    # 返回单词对应的id列表
    return [word_to_id[word] for word in data if word in word_to_id]


def raw_data(data_path=None, vocab_size=10000):
    train_path = os.path.join(data_path, 'emoji.train.txt')
    valid_path = os.path.join(data_path, 'emoji.valid.txt')
    test_path = os.path.join(data_path, 'emoji.test.txt')

    word_to_id = _build_vocab(train_path, vocab_size)
    train_data = _file_to_word_ids(train_path, word_to_id)
    valid_data = _file_to_word_ids(valid_path, word_to_id)
    test_data = _file_to_word_ids(test_path, word_to_id)
    vocabulary = len(word_to_id)
    return train_data, valid_data, test_data, vocabulary


def data_producer(raw_data, batch_size, num_steps, name=None):
    """Iterate on the raw data.

    This chunks up raw_data into batches of examples and returns Tensors that
    are drawn from these batches.

    Args:
      raw_data: one of the raw data outputs from raw_data.
      batch_size: int, the batch size.
      num_steps: int, the number of unrolls.
      name: the name of this operation (optional).

    Returns:
      A pair of Tensors, each shaped [batch_size, num_steps]. The second element
      of the tuple is the same data time-shifted to the right by one.

    Raises:
      tf.errors.InvalidArgumentError: if batch_size or num_steps are too high.
    """
    with tf.name_scope(name, 'DATAProducer', [raw_data, batch_size, num_steps]):
        raw_data = tf.convert_to_tensor(raw_data, name='raw_data', dtype=tf.int32)

        data_len = tf.size(raw_data)
        batch_len = data_len // batch_size

        # data是一个batch_size行，batch_len列的二维tensor，每一行是一个batch数据
        data = tf.reshape(raw_data[0: batch_size * batch_len],
                          [batch_size, batch_len])

        epoch_size = (batch_len - 1) // num_steps
        assertion = tf.assert_positive(
            epoch_size,
            message='epoch_size == 0, decrease batch_size or num_steps')
        with tf.control_dependencies([assertion]):
            epoch_size = tf.identity(epoch_size, name='epoch_size')

        # 什么意思？ 多线程读取数据 参考这个http://blog.csdn.net/lyg5623/article/details/69387917
        i = tf.train.range_input_producer(epoch_size, shuffle=False).dequeue()
        x = tf.strided_slice(data, [0, i * num_steps],
                             [batch_size, (i + 1) * num_steps])
        x.set_shape([batch_size, num_steps])
        y = tf.strided_slice(data, [0, i * num_steps + 1],
                             [batch_size, (i + 1) * num_steps + 1])
        y.set_shape([batch_size, num_steps])
        return x, y


if __name__ == '__main__':
    _read_words('./data/emoji.train.txt')

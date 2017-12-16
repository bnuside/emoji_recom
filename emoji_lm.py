# based on PTB Model
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time

import numpy as np
import tensorflow as tf

import reader
import random
import sample_data
from Model import Model
from Config import Config, TestConfig, DebugConfig

from tensorflow.python.client import device_lib

flags = tf.flags
logging = tf.logging

flags.DEFINE_string(
    'model', 'train',
    'train or test model')
flags.DEFINE_string('data_path', 'data/',
                    'Where the training/test data is stored.')
flags.DEFINE_string('save_path', 'saved_model/',
                    'Model output directory.')
flags.DEFINE_bool('clean_data', False, 'Since data cleaned, no need to do it again while not necessary')
flags.DEFINE_integer('num_gpus', 0,
                     'If larger than 1, Grappler AutoParallel optimizer '
                     'will create multiple training replicas with each GPU '
                     'running one replica.')
flags.DEFINE_string('rnn_mode', None,
                    'The low level implementation of lstm cell: one of CUDNN, '
                    'BASIC, and BLOCK, representing cudnn_lstm, basic_lstm, '
                    'and lstm_block_cell classes.')
flags.DEFINE_bool('emoji_only', False, 'data clean make emoji only')
flags.DEFINE_string('test_path', 'data/emoji.test.txt', 'for calculate predict acculate')
flags.DEFINE_bool('predict', False, 'used to predict next word with trained model')
flags.DEFINE_bool('debug', False, 'used for debug')
FLAGS = flags.FLAGS
BASIC = "basic"
BLOCK = "block"


class DataInput(object):
    """The input data."""

    def __init__(self, config, data, name=None):
        self.batch_size = batch_size = config.batch_size
        self.num_steps = num_steps = config.num_steps
        self.epoch_size = ((len(data) // batch_size) - 1) // num_steps
        self.input_data, self.targets = reader.data_producer(
            data, batch_size, num_steps, name=name)


def run_epoch(session, model, eval_op=None, verbose=False):
    """Runs the model on the given data."""
    start_time = time.time()
    costs = 0.0
    iters = 0
    state = session.run(model.initial_state)

    fetches = {
        'cost': model.cost,
        'final_state': model.final_state
    }
    if model.model_type == 'test':
        fetches = {
            'cost': model.cost,
            'final_state': model.final_state,
            'logits': model.logits,
            'y': model.y
        }
        top3_hit = 0
        top1_hit = 0
        total = model.input.epoch_size
    if eval_op is not None:
        fetches['eval_op'] = eval_op

    for step in range(model.input.epoch_size):
        feed_dict = {}
        for i, (c, h) in enumerate(model.initial_state):
            feed_dict[c] = state[i].c
            feed_dict[h] = state[i].h

        vals = session.run(fetches, feed_dict)
        cost = vals['cost']
        state = vals['final_state']

        if model.model_type == 'test':

            logits = vals['logits']
            y = vals['y']

            if np.argmax(logits) == y:
                top1_hit += 1

            t3_logits = []

            for i in range(3):
                t3_logits.append(np.argmax(logits))
                logits[t3_logits[i]] = -len(logits) + i

            if y in t3_logits:
                top3_hit += 1

        costs += cost
        iters += model.input.num_steps
        if verbose and step % (model.input.epoch_size // 10) == 10:
            print('%.3f perplexity: %.3f speed: %.0f wps' %
                  (step * 1.0 / model.input.epoch_size, np.exp(costs / iters),
                   iters * model.input.batch_size * max(1, FLAGS.num_gpus) /
                   (time.time() - start_time)))

    if model.model_type == 'test':
        print('top1: ', top1_hit / total)
        print('top3: ', top3_hit / total)
    return np.exp(costs / iters)


def get_config():
    """Get model config."""
    config = None
    if FLAGS.model == 'train':
        config = Config()
        if FLAGS.debug:
            config = DebugConfig()
    elif FLAGS.model == 'test':
        config = TestConfig()
    else:
        raise ValueError('Invalid model: %s', FLAGS.model)
    if FLAGS.rnn_mode:
        config.rnn_mode = FLAGS.rnn_mode
    if FLAGS.num_gpus != 1 or tf.__version__ < '1.3.0':
        config.rnn_mode = BASIC
    return config


def main(_):
    if not FLAGS.data_path:
        raise ValueError('Must set --data_path to data directory')
    gpus = [
        x.name for x in device_lib.list_local_devices() if x.device_type == 'GPU'
        ]
    if FLAGS.num_gpus > len(gpus):
        raise ValueError(
            'Your machine has only %d gpus '
            'which is less than the requested --num_gpus=%d.'
            % (len(gpus), FLAGS.num_gpus))

    if FLAGS.clean_data:
        sample_data.clean_data(FLAGS.data_path, emoji_only=FLAGS.emoji_only)
    config = get_config()
    eval_config = get_config()
    eval_config.batch_size = 1
    eval_config.num_steps = 1

    raw_data = reader.raw_data(FLAGS.data_path, config.vocab_size, FLAGS.clean_data)
    train_data, valid_data, test_data, _ = raw_data

    with tf.Graph().as_default():
        initializer = tf.random_uniform_initializer(-config.init_scale,
                                                    config.init_scale)

        with tf.name_scope('Train'):
            train_input = DataInput(config=config, data=train_data, name='TrainInput')
            with tf.variable_scope('Model', reuse=None, initializer=initializer):
                m = Model(model_type='train', config=config, input_=train_input, num_gpus=FLAGS.num_gpus)
            tf.summary.scalar('Training Loss', m.cost)
            tf.summary.scalar('Learning Rate', m.lr)

        with tf.name_scope('Valid'):
            valid_input = DataInput(config=config, data=valid_data, name='ValidInput')
            with tf.variable_scope('Model', reuse=True, initializer=initializer):
                mvalid = Model(model_type='valid', config=config, input_=valid_input, num_gpus=FLAGS.num_gpus)
            tf.summary.scalar('Validation Loss', mvalid.cost)

        with tf.name_scope('Test'):
            test_input = DataInput(
                config=eval_config, data=test_data, name='TestInput')
            with tf.variable_scope('Model', reuse=True, initializer=initializer):
                mtest = Model(model_type='test', config=eval_config,
                              input_=test_input, num_gpus=FLAGS.num_gpus)

        models = {'Train': m, 'Valid': mvalid, 'Test': mtest}
        for name, model in models.items():
            model.export_ops(name)
        metagraph = tf.train.export_meta_graph()

    with tf.Graph().as_default():
        tf.train.import_meta_graph(metagraph)
        for model in models.values():
            model.import_ops()
        sv = tf.train.Supervisor(logdir=FLAGS.save_path)
        with sv.managed_session() as session:

            if FLAGS.predict:
                print('predicting')
                run_epoch(session, mtest)
                return

            else:
                for i in range(config.max_max_epoch):
                    lr_decay = config.lr_decay ** max(i + 1 - config.max_epoch, 0.0)
                    m.assign_lr(session, config.learning_rate * lr_decay)

                    print('Epoch: %d Learning rate: %.3f' % (i + 1, session.run(m.lr)))
                    train_perplexity = run_epoch(session, m, eval_op=m.train_op,
                                                 verbose=True)
                    print('Epoch: %d Train Perplexity: %.3f' % (i + 1, train_perplexity))
                    valid_perplexity = run_epoch(session, mvalid)
                    print('Epoch: %d Valid Perplexity: %.3f' % (i + 1, valid_perplexity))

            test_perplexity = run_epoch(session, mtest)
            print('Test Perplexity: %.3f' % test_perplexity)

            if FLAGS.save_path:
                print('Saving model to %s.' % FLAGS.save_path)
                sv.saver.save(session, FLAGS.save_path, global_step=sv.global_step)

    print('finished')


if __name__ == '__main__':
    tf.app.run()

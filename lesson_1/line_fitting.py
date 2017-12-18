import tensorflow as tf
import numpy as np


def demo(scale=1, train_loops=1000):
    # graph
    weights = tf.Variable([-1.0])
    biases = tf.Variable([-1.0])
    x_input = tf.placeholder(tf.float32)
    y_target = tf.placeholder(tf.float32)
    y = tf.multiply(weights, x_input) + biases

    loss = tf.reduce_mean(tf.square(y - y_target))
    optimizer = tf.train.AdamOptimizer(learning_rate=0.1)
    train = optimizer.minimize(loss)
    init = tf.global_variables_initializer()

    # data
    x_data = np.random.rand(100).astype(np.float32)*scale
    y_data = x_data * 0.1 + 0.3

    # init
    sess = tf.Session()
    sess.run(init)

    # train
    for step in range(train_loops):
        fetches = {
            "weights": weights,
            "bias": biases,
            "train": train,
            "loss": loss,
            "x": x_input,
            "y": y,
        }

        vals = sess.run(fetches, {x_input: x_data, y_target: y_data})
        if (step + 1) % 10 == 0:
            print(step, vals["weights"], vals["bias"], vals["loss"])
    return

if __name__ == '__main__':
    demo(100, 1000)

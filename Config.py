class Config(object):
    """model config."""
    init_scale = 0.05
    learning_rate = 1.0
    max_grad_norm = 5
    num_layers = 2
    num_steps = 35
    hidden_size = 650
    max_epoch = 16
    max_max_epoch = 35
    keep_prob = 0.5
    lr_decay = 0.8
    batch_size = 25
    vocab_size = 12000
    rnn_mode = 'basic'


class DebugConfig:
    """model config."""
    init_scale = 0.05
    learning_rate = 1.0
    max_grad_norm = 5
    num_layers = 2
    num_steps = 15
    hidden_size = 100
    max_epoch = 2
    max_max_epoch = 5
    keep_prob = 0.5
    lr_decay = 0.8
    batch_size = 25
    vocab_size = 1000
    rnn_mode = 'basic'


class TestConfig(object):
    """Tiny config, for testing."""
    init_scale = 0.1
    learning_rate = 1.0
    max_grad_norm = 1
    num_layers = 1
    num_steps = 2
    hidden_size = 2
    max_epoch = 1
    max_max_epoch = 1
    keep_prob = 1.0
    lr_decay = 0.5
    batch_size = 25
    vocab_size = 12000
    rnn_mode = 'basic'

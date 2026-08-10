# -*- coding: utf-8 -*-

import torch.nn as nn


class Model(nn.Module):
    def __init__(self, window_size, input_size, hidden_size, num_layers, dropout_prob):
        super(Model, self).__init__()
        self.window_size = window_size
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout_prob = dropout_prob

        self.lstm = nn.LSTM(input_size=self.input_size,
                            hidden_size=self.hidden_size,
                            num_layers=self.num_layers,
                            batch_first=True,
                            dropout=self.dropout_prob,
                            bidirectional=True)
        self.dense = nn.Linear(2 * self.hidden_size, 1)

    def forward(self, inputs):
        """
        inputs: (batch_size, window_size, input_size)
        outputs: (batch_size)
        """
        hidden_states, _ = self.lstm(inputs)  # (batch_size, window_size, 2*hidden_size)
        last_hidden_states = hidden_states[:, -1, :]  # (batch_size, 2*hidden_size)
        outputs = self.dense(last_hidden_states)  # (batch_size, 1)
        outputs = outputs.squeeze(1)  # (batch_size)
        return outputs

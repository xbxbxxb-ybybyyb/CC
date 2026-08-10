# -*- coding: utf-8 -*-

import torch
import numpy as np
from torch.utils.data import Dataset as TorchDataset


class Dataset(TorchDataset):
    def __init__(self, window_size, input_size):
        self.window_size = window_size
        self.input_size = input_size
        self.x = None  # (num_samples, feature_size)
        self.y = None  # (num_samples)
        self.num_samples = 0

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return self.get_item(idx)

    def load_data(self, x, y):
        """
        x: (num_samples, feature_size)
        y: (num_samples)
        """
        self.x = x
        self.y = y
        self.num_samples = x.shape[0]

    def get_item(self, idx):
        """
        inputs: (window_size, input_size)
        targets: (1)
        """
        inputs = np.zeros([self.window_size, self.input_size], dtype=np.float32)
        x_head_idx = max(idx - self.window_size + 1, 0)
        x_tail_idx = idx
        f_head_idx = self.window_size - (x_tail_idx - x_head_idx + 1)
        f_tail_idx = self.window_size - 1
        inputs[f_head_idx:f_tail_idx + 1] = self.x[x_head_idx:x_tail_idx + 1]
        if self.y is None:
            targets = 0.0
        else:
            targets = self.y[idx]
        item = {
            "inputs": torch.tensor(inputs, dtype=torch.float32),
            "targets": torch.tensor(targets, dtype=torch.float32),
        }
        return item

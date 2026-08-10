import torch
import numpy as np
from torch.utils.data import Dataset as TorchDataset


class Dataset2D(TorchDataset):
    def __init__(self, x, y):
        self.x = x  # (num_samples, num_factors)
        self.y = y  # (num_samples) / None
        self.num_samples = x.shape[0]
        self.num_factors = x.shape[1]
        if self.y is None:
            self.y = np.zeros([self.num_samples], dtype=np.float)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, i):
        x = self.x[i]
        y = self.y[i]

        x = torch.tensor(x, dtype=torch.float)  # (batch_size, num_factors)
        y = torch.tensor(y, dtype=torch.float)  # (batch_size)
        return x, y


class Dataset3D(TorchDataset):
    def __init__(self, x, y, window_size):
        self.x = x  # (num_samples, num_factors)
        self.y = y  # (num_samples) / None
        self.window_size = window_size
        self.num_samples = x.shape[0]
        self.num_factors = x.shape[1]
        if self.y is None:
            self.y = np.zeros([self.num_samples], dtype=np.float)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, i):
        n_data = min(i + 1, self.window_size)
        n_zero = self.window_size - n_data
        x_zero = np.zeros([n_zero, self.num_factors], dtype=np.float)  # (n_zero, num_factors)
        x_data = self.x[i + 1 - n_data:i + 1]  # (n_data, num_factors)
        x = np.concatenate([x_zero, x_data], axis=0)  # (window_size, num_factors)
        y = self.y[i]

        x = torch.tensor(x, dtype=torch.float)  # (batch_size, window_size, num_factors)
        y = torch.tensor(y, dtype=torch.float)  # (batch_size)
        return x, y

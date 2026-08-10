import torch
from torch.utils.data import Dataset

__all__ = ['Dataset2D']


class Dataset2D(Dataset):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __len__(self):
        return self.x.shape[0]

    def __getitem__(self, idx):
        inputs = self.x[idx]
        outputs = self.y[idx]
        item = {
            'x': torch.tensor(inputs, dtype=torch.float32),  # (batch_size, x.shape[1])
            'y_true': torch.tensor(outputs, dtype=torch.float32)  # (batch_size, )
        }
        return item

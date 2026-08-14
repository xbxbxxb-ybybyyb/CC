# coding: utf-8
# Author：fengchi863
# Date ：2023/12/14 15:38

from torch.utils.data import Dataset


class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def to_python_float(t):
    if hasattr(t, 'item'):
        return t.item()
    else:
        return t[0]


def clip_gradient(optimizer, grad_clip):
    for group in optimizer.param_groups:
        for param in group['params']:
            if param.grad is not None:
                param.grad.data.clamp_(-grad_clip, grad_clip)


class BaseDataset(Dataset):
    def __init__(self, x, y=None):
        self.X = x
        self.Y = y
        self.size = len(self.X)

    def __getitem__(self, index):
        x = self.X[index, :]
        if self.Y is None:
            return x
        else:
            y = self.Y[index]
            return x, y

    def __len__(self):
        return self.size


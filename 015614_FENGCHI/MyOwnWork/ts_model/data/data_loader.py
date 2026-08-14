import os

import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler
from torch.utils.data import Dataset, DataLoader, TensorDataset, Subset


class TimeseriesData(object):
    def __init__(self,
                 root_path='/data/user/015614/MyOwnWork/ts_model/archive/',
                 data_path='archive/AAPL.csv',
                 timestamp='2021-04-23 00:00:00'
                 ):
        self.root_path = root_path
        self.data_path = data_path
        self.timestamp = timestamp
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.dataset = self.__read()
        self._values_cache = None
        self._labels_cache = None

    def __len__(self):
        return len(self.dataset)

    def __read(self):
        return pd.read_csv(
            os.path.join(self.root_path, self.data_path), index_col=0,
            parse_dates=True).loc[self.timestamp:]

    def values(self):
        # 如果缓存中已经存储了值，则直接返回缓存的值
        if self._values_cache is None:
            data = self.dataset.drop(['Adj Close', 'Volume'], axis=1).values
            self._values_cache = self.scaler.fit_transform(data)
        return self._values_cache

    def labels(self):
        # 如果缓存中已经存储了标签，则直接返回缓存的标签
        if self._labels_cache is None:
            targets = self.dataset['Close'].values.reshape(-1, 1)
            self._labels_cache = self.scaler.fit_transform(targets)
        return self._labels_cache


class SupervisedTimeseriesData(TimeseriesData):
    def __init__(self, lag: int = 10):
        super(SupervisedTimeseriesData, self).__init__()
        self.lag = lag
        self._supervised_values_cache = None
        self._supervised_labels_cache = None

    @property
    def supervised_values(self):
        if self._supervised_values_cache is None:
            self._supervised_values_cache = self._compute_supervised_values()
        return self._supervised_values_cache

    @property
    def supervised_labels(self):
        if self._supervised_labels_cache is None:
            self._supervised_labels_cache = self._compute_supervised_labels()
        return self._supervised_labels_cache

    def _compute_supervised_values(self):
        x = [self.values()[i:i + self.lag] for i in range(self.__len__() - self.lag)]
        return torch.tensor(np.array(x), dtype=torch.float)

    def _compute_supervised_labels(self):
        return torch.tensor(self.labels()[self.lag:], dtype=torch.float)


class SupervisedTimeseriesDataset(Dataset):
    def __init__(self):
        super(SupervisedTimeseriesDataset, self).__init__()
        self.set = SupervisedTimeseriesData(lag=30)
        self.dataset = TensorDataset(self.set.supervised_values, self.set.supervised_labels)
        self.train_idx = list(range(self.__len__() * 3 // 5))
        self.val_idx = list(range(self.__len__() * 3 // 5, self.__len__() * 4 // 5))
        self.test_idx = list(range(self.__len__() * 4 // 5, self.__len__()))

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, index):
        return self.set.supervised_values[index], self.set.supervised_labels[index]

    @property
    def train_set(self):
        return Subset(self.dataset, indices=self.train_idx)

    @property
    def val_set(self):
        return Subset(self.dataset, indices=self.val_idx)

    @property
    def test_set(self):
        return Subset(self.dataset, indices=self.test_idx)


ts = TimeseriesData()
print(ts.values())
print(ts.labels())
print(ts.__len__())
sv = SupervisedTimeseriesData(lag=10)
print(sv.values().shape)
print(sv.labels().shape)

svd = SupervisedTimeseriesDataset()
print(svd.__len__())
print(len(svd.train_set), len(svd.val_set), len(svd.test_set))
print(svd.val_set)

train_loader = DataLoader(svd.train_set, batch_size=32, shuffle=True)
valid_loader = DataLoader(dataset=svd.val_set, batch_size=32, shuffle=False)
test_loader = DataLoader(dataset=svd.test_set, batch_size=32, shuffle=False)

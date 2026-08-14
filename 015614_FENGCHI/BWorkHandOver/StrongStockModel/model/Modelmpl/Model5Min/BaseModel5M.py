from dataApi.tradeDate import get_date_range, get_pre_trade_date
from keras.models import load_model
from tqdm import tqdm
import pandas as pd
import numpy as np
import time
import os


from sklearn.linear_model import LinearRegression

class Factor5MinLoader(object):

    def __init__(self, start_date=20170103, end_date=20181231, freq=48, model_time_len=1, factor_list=None,
                 load_address='/data/group/800319/junkBigFactorPool/back_factor/'):

        idx_date = np.load('%s/idx_date.npy' % load_address)
        idx_time = np.load('%s/idx_time.npy' % load_address)
        idx_code = np.load('%s/idx_code.npy' % load_address)
        idx_len = idx_date.shape[0]
        time_len = idx_time.shape[0]

        date_list = get_date_range(start_date, end_date)
        start_date = max(date_list[0], idx_date[0])
        end_date = min(date_list[-1], idx_date[-1])
        date_list = get_date_range(start_date, end_date)

        date_list_index = (np.r_[1, np.diff(idx_date)] > 0) & (idx_date >= start_date) & (
                idx_date <= get_pre_trade_date(end_date, -1))
        date_list_index = np.arange(date_list_index.shape[0])[date_list_index]
        date_list_index = date_list_index if date_list[-1] < idx_date[-1] else np.r_[
            date_list_index, len(idx_date)]

        if not isinstance(factor_list, list):
            raise ValueError("Factor list must be given.")
        factor_num = len(factor_list)

        self.idx_date = idx_date
        self.idx_time = idx_time
        self.idx_code = idx_code
        self.idx_len = idx_len
        self.time_len = time_len

        self.date_list = date_list
        self.start_date = start_date
        self.end_date = end_date
        self.freq = freq
        self.factor_list = factor_list
        self.model_time_len = model_time_len

        self.factor_num = factor_num
        self.load_address = load_address
        self.date_list_index = date_list_index

    def split_train_test(self, start_date, end_date, test_date_idx):
        test_dates = [get_pre_trade_date(end_date, ~ x) for x in sorted(test_date_idx)]
        start_idx = self.date_list_index[self.date_list.index(start_date)]
        end_idx = self.date_list_index[self.date_list.index(end_date) + 1]
        test_idx = np.r_[tuple(np.arange(self.date_list_index[self.date_list.index(x)], self.date_list_index[
            self.date_list.index(x) + 1]) for x in test_dates)]
        train_idx = sorted(list(set(np.arange(start_idx, end_idx)) - set(test_idx)))
        return train_idx, test_idx

    def load_data(self, start_date, end_date=0, return_idx=False):

        if end_date:
            start_idx = self.date_list_index[self.date_list.index(start_date)]
            end_idx = self.date_list_index[self.date_list.index(end_date) + 1]
            idx_len = end_idx - start_idx
            idx_slice = slice(start_idx, end_idx)
        else:
            idx_len = len(start_date)
            idx_slice = start_date

        X = np.empty((self.factor_num, idx_len, self.freq + self.model_time_len - 1), dtype=np.float32)

        for idx in range(self.factor_num):
        # for idx in tqdm(range(self.factor_num), desc='Factor_loading...'):
            fp = np.memmap('%s/%s.npy' % (
                self.load_address, self.factor_list[idx]), dtype='float32', mode='r', shape=(
                self.idx_len, self.time_len), offset=128)
            X[idx] = fp[idx_slice, 1 - self.freq - self.model_time_len:]
            del fp

        y = np.memmap('%s/%s.npy' % (self.load_address, 'future'), dtype='float32', mode='r', shape=(
            self.idx_len, self.freq), offset=128)
        y = y[idx_slice]
        y = y.flatten()

        nolimit = np.memmap('%s/%s.npy' % (self.load_address, 'nolimit'), dtype='bool', mode='r', shape=(
            self.idx_len, self.freq), offset=128)
        nolimit = nolimit[idx_slice]
        nolimit = nolimit.flatten()

        if self.model_time_len > 1:
            X = np.lib.stride_tricks.as_strided(X, shape=(X.shape[0], X.shape[1], self.freq, X.shape[2] - self.freq + 1),
                                                strides=(X.strides[0], X.strides[1], X.strides[2], X.strides[2]))
            X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], X.shape[3]).transpose(1, 2, 0)
        else:
            X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], 1).transpose(1, 2, 0)

        if not return_idx:
            return X, y, nolimit
        else:
            idx_date = self.idx_date[idx_slice, None].repeat(self.freq, axis=1).flatten()
            idx_code = self.idx_code[idx_slice, None].repeat(self.freq, axis=1).flatten()
            idx_time = self.idx_time[None, -self.freq:].repeat(idx_len, axis=0).flatten()
            return X, y, nolimit, idx_date, idx_time, idx_code

    def feature_engineering(self, X, y, *args, nolimit=None, limit=0.2, drop_time_idx=None):

        valid = (np.isclose(X, 0).sum(axis=2) < limit * X.shape[2]).all(axis=1) & np.isfinite(y)
        if nolimit is not None:
            valid &= nolimit

        if drop_time_idx:
            drop_time_idx = list(drop_time_idx)
            _time_idx = np.full(self.freq, True, dtype=bool)
            _time_idx[drop_time_idx] = False
            _time_idx = np.repeat(_time_idx[None, :], len(y) // len(_time_idx), axis=0).flatten()
            valid &= _time_idx

        valid_samples = valid.sum()
        print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
            valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))

        X = X[valid]
        y = y[valid]

        if X.shape[1] == 1:
            X = X[:, 0]

        dic = {}
        for arg in range(len(args)):
            dic[arg] = args[arg].flatten()[valid]

        return (X, y) + tuple(dic.values())

    def lazy_reach_data(self, train_start, train_end, predict_start, predict_end, test_date_idx, limit=0.4):

        train_idx, test_idx = self.split_train_test(train_start, train_end, test_date_idx)

        X_train, y_train, nolimit_train,d_train,t_train,c_train = self.load_data(train_idx, 0,True)
        X_test, y_test, nolimit_test, d_test, t_test, c_test = self.load_data(test_idx, 0, True)
        X_pred, y_pred, nolimit_pred, d_pred, t_pred, c_pred = self.load_data(predict_start, predict_end, True)

        X_train, y_train,d_train,t_train,c_train = self.feature_engineering(X_train, y_train,d_train,t_train,c_train, nolimit=nolimit_train, limit=limit)
        X_test, y_test, d_test, t_test, c_test = self.feature_engineering(
            X_test, y_test, d_test, t_test, c_test, nolimit=nolimit_test, limit=limit)
        X_pred, y_pred, d_pred, t_pred, c_pred = self.feature_engineering(
            X_pred, y_pred, d_pred, t_pred, c_pred, nolimit=nolimit_pred, limit=limit)

        return X_train, y_train,d_train,t_train,c_train, X_test, y_test, d_test, t_test, c_test, X_pred, y_pred, d_pred, t_pred, c_pred

    def load_fix_point(self,X,y,idx_date,idx_time,idx_code,factor_list,bar_list = [1000,1030,1100,1300,1330,1400,1430]):
        judge = np.zeros(idx_date.shape)>0
        for each in bar_list:
            judge = judge | (idx_time==each)
        X, y, idx_date, idx_time, idx_code = X[judge],y[judge],idx_date[judge],idx_time[judge],idx_code[judge]
        index = pd.MultiIndex.from_tuples(list(zip(idx_date,idx_time,idx_code)))
        X,y = pd.DataFrame(X,index=index,columns=factor_list),pd.DataFrame({'actual_label':y},index=index)
        return X, y#, idx_date, idx_time, idx_code
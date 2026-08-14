from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date
from tqdm import tqdm
import numpy as np
import time
import pandas as pd
import itertools
import os


class FixFactorRollPrepare(object):

    def __init__(self, start_date=20140801, end_date=20201031, freq=7, model_time_len=7, factor_list=None,
                 load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/'):

        idx_date = np.load('%s/idx_date.npy' % load_address)
        idx_time = np.load('%s/idx_time.npy' % load_address)
        idx_code = np.load('%s/idx_code.npy' % load_address)

        _select = (idx_date >= start_date) & (idx_date <= end_date)
        idx_date = idx_date[_select]
        idx_code = idx_code[_select]
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
        self.model_time_len = model_time_len
        self.factor_list = factor_list
        self.factor_num = factor_num
        self.load_address = load_address
        self.date_list_index = date_list_index

    def load_data(self, start_date, end_date=0, future_end=True, return_idx=False):

        start_idx = self.date_list_index[self.date_list.index(start_date)]
        end_idx = self.date_list_index[self.date_list.index(end_date) + 1]
        future_end_idx = end_idx if future_end else self.date_list_index[self.date_list.index(end_date)]
        future_idx_len = self.idx_date[self.idx_date <= end_date].shape[
            0] if future_end else self.idx_date[self.idx_date < end_date].shape[0]
        X = np.empty((self.factor_num, end_idx - start_idx, self.freq + self.model_time_len - 1), dtype=np.float32)

        # for idx in range(self.factor_num):
        for idx in tqdm(range(self.factor_num), desc='Factor_loading...'):
            fp = np.memmap('%s/%s.npy' % (self.load_address, self.factor_list[idx]),
                           dtype='float32', mode='r', shape=(self.idx_len, self.time_len), offset=128)
            X[idx] = fp[start_idx: end_idx, 1 - self.freq - self.model_time_len:]
            del fp

        y = np.memmap('%s/%s.npy' % (self.load_address, 'future'),
                      dtype='float32', mode='r', shape=(future_idx_len, self.freq), offset=128)
        y = y[start_idx: future_end_idx]

        nolimit = np.memmap('%s/%s.npy' % (self.load_address, 'nolimit'), dtype='bool', mode='r', shape=(
            self.idx_len, self.freq), offset=128)
        nolimit = nolimit[start_idx: end_idx]

        if not return_idx:
            return X, y, nolimit
        else:
            idx_date = self.idx_date[start_idx: end_idx, None].repeat(self.freq, axis=1)
            idx_code = self.idx_code[start_idx: end_idx, None].repeat(self.freq, axis=1)
            idx_time = self.idx_time[None, -self.freq:].repeat(idx_date.shape[0], axis=0)
            return X, y, nolimit, idx_date, idx_time, idx_code

    def load_custom_pool(self, pool_name, start_date, end_date=0):

        if pool_name[0] != '_':
            raise ValueError('Name of custom pool must start with _ to be different from normal factors.')

        start_idx = self.date_list_index[self.date_list.index(start_date)]
        end_idx = self.date_list_index[self.date_list.index(end_date) + 1]

        custom_pool = np.memmap('%s/%s.npy' % (self.load_address, pool_name), dtype='bool', mode='r', shape=(
            self.idx_len, self.freq), offset=128)
        custom_pool = custom_pool[start_idx: end_idx]

        return custom_pool

    def feature_engineering(self, X, y, nolimit, *args, limit=0.2, custom_pool=None):

        if self.model_time_len > 1:

            X = np.lib.stride_tricks.as_strided(X, shape=(X.shape[0], X.shape[1], self.freq, X.shape[2] - self.freq + 1),
                                                strides=(X.strides[0], X.strides[1], X.strides[2], X.strides[2]))
            X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], X.shape[3]).transpose(1, 2, 0)

        else:
            X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], self.model_time_len).transpose(1, 2, 0)

        y = y.flatten()
        nolimit = nolimit.flatten()
        valid = (np.isclose(X, 0).sum(axis=2) < limit * X.shape[2]).all(axis=1) & np.isfinite(y) & nolimit

        if custom_pool:
            valid &= custom_pool

        valid_samples = valid.sum()
        print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
            valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))

        X = X[valid]
        y = y[valid]

        dic = {}
        for arg in range(len(args)):
            dic[arg] = args[arg].flatten()[valid]

        if self.model_time_len == 1:
            X = X[:, 0]

        return (X, y) + tuple(dic.values())


def load_5min_data(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                   model_time_len=1, target_point=[1000, 1030, 1100, 1300, 1330, 1400, 1430, 1455],
                   address='/arch1/group/800442/800319/HFfactor/DTC2021/data/', nolimit_tag='nolimit',freq = 48):
    # factor_list = ['20201203152143557']
    print(f'freq {freq}')
    print(f'load from {address}')
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)
    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    idx_time = np.load('%s/idx_time.npy' % address)
    time_idx_map = [idx_time[-freq:].tolist().index(x) - freq for x in target_point]
    if max(time_idx_map)>0:
        raise Exception('Unexpected time_idx_map')

    time_len = idx_time.shape[0]

    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1

    if return_idx:
        idx_date = idx_date[choose, None].repeat(len(target_point), axis=1)
        idx_code = idx_code[choose, None].repeat(len(target_point), axis=1)
        idx_time = idx_time[None, time_idx_map].repeat(choose.sum(), axis=0)

    fp = np.memmap(f'{address}/future.npy', dtype='float32', mode='r', offset=128)
    real_y_shape = fp.shape[0] // freq - starts
    del fp
    real_y_shape = 0 if real_y_shape < 0 else (real_y_shape if real_y_shape < shape else shape)
    real_y_choose = (np.arange(choose[:starts + real_y_shape].shape[0])[choose[:starts + real_y_shape]] - starts).tolist()
    real_y_choose = slice(None) if len(real_y_choose) == real_y_shape else real_y_choose

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    X = np.empty((len(factor_list), len(choose), len(target_point)), dtype=np.float32)
    y = np.empty((len(choose), len(target_point)), dtype=np.float32)
    nolimit = np.empty((len(choose), len(target_point)), dtype=np.bool)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/{f}.npy', dtype='float32', mode='r',
                       shape=(shape, time_len), offset=starts * time_len * 4 + 128)
        X[j] = fp[choose, time_idx_map]
        del fp

    if not real_y_shape:
        y[:] = np.nan
        nolimit[:] = False
    else:
        fp = np.memmap(f'{address}/future.npy', dtype='float32', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq * 4 + 128)
        y[:real_y_shape] = fp[real_y_choose, time_idx_map]
        y[real_y_shape:] = np.nan

        fp = np.memmap(f'{address}/{nolimit_tag}.npy', dtype='bool', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq + 128)
        nolimit[:real_y_shape] = fp[real_y_choose, time_idx_map]
        nolimit[real_y_shape:] = False

    if return_idx:
        return X, y, nolimit, idx_date, idx_code, idx_time
    else:
        return X, y, nolimit

def load_fix_data(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                  model_time_len=1, freq=7, address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/', nolimit_tag='nolimit'):
    print(f'load from {address}')
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    idx_time = np.load('%s/idx_time.npy' % address)

    time_len = idx_time.shape[0]

    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1

    if return_idx:
        idx_date = idx_date[choose, None].repeat(freq + model_time_len - 1, axis=1)
        idx_code = idx_code[choose, None].repeat(freq + model_time_len - 1, axis=1)
        idx_time = idx_time[None, 1 - freq - model_time_len:].repeat(choose.sum(), axis=0)

    fp = np.memmap(f'{address}/future.npy', dtype='float32', mode='r', offset=128)
    real_y_shape = fp.shape[0] // freq - starts
    del fp
    real_y_shape = 0 if real_y_shape < 0 else (real_y_shape if real_y_shape < shape else shape)
    real_y_choose = (np.arange(choose[:starts + real_y_shape].shape[0])[choose[:starts + real_y_shape]] - starts).tolist()
    real_y_choose = slice(None) if len(real_y_choose) == real_y_shape else real_y_choose

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    X = np.empty((len(factor_list), len(choose), freq + model_time_len - 1), dtype=np.float32)
    y = np.empty((len(choose), freq), dtype=np.float32)
    nolimit = np.empty((len(choose), freq), dtype=np.bool)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/{f}.npy', dtype='float32', mode='r',
                       shape=(shape, time_len), offset=starts * time_len * 4 + 128)
        X[j] = fp[choose, 1 - freq - model_time_len:]
        del fp

    if not real_y_shape:
        y[:] = np.nan
        nolimit[:] = False
    else:
        fp = np.memmap(f'{address}/future.npy', dtype='float32', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq * 4 + 128)
        y[:real_y_shape] = fp[real_y_choose, :]
        y[real_y_shape:] = np.nan

        fp = np.memmap(f'{address}/{nolimit_tag}.npy', dtype='bool', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq + 128)
        nolimit[:real_y_shape] = fp[real_y_choose, :]
        nolimit[real_y_shape:] = False

    if return_idx:
        return X, y, nolimit, idx_date, idx_code, idx_time
    else:
        return X, y, nolimit


def load_fix_data_selfdefined_label(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                                    model_time_len=1, freq=7, address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/', nolimit_tag='nolimit',
                                    label_path=None, return_1day_label=False):
    print(label_path)
    print(f'loading from {start_date} to {end_date}')
    X, y_1day, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=start_date, end_date=end_date, factor_list=factor_list,
                                                                     code_list=code_list, return_idx=return_idx, model_time_len=model_time_len,
                                                                     freq=freq, address=address, nolimit_tag=nolimit_tag)
    l_path, l_name = os.path.split(label_path)
    y, _, _, _, _, _ = load_fix_data(start_date=start_date, end_date=end_date, factor_list=[l_name.replace('.npy', '')],
                                     code_list=code_list, return_idx=return_idx,
                                     freq=freq, address=l_path, nolimit_tag=nolimit_tag)
    if return_1day_label:
        return X, y[0, :, :], nolimit, idx_date, idx_code, idx_time, y_1day

    return X, y[0, :, :], nolimit, idx_date, idx_code, idx_time


def load_5min_8bar_with_selfdeined_label(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                                         model_time_len=1, address='/arch1/group/800442/800319/HFfactor/DTC2021/data/', nolimit_tag='nolimit',
                                         label_path=None, return_1day_label=False,freq=48):
    l_path, l_name = os.path.split(label_path)
    X, y, nolimit, idx_date, idx_code, idx_time = load_5min_data(get_pre_trade_date(start_date), end_date, factor_list=factor_list, code_list=code_list,
                                                                 model_time_len=model_time_len, address=address, nolimit_tag=nolimit_tag, return_idx=return_idx,freq=freq)
    nolimit[idx_time == 1455] = True
    y_self_define, _, _, _, _, _ = load_5min_data(get_pre_trade_date(start_date), end_date, factor_list=[l_name.replace('.npy', '')], code_list=code_list,
                                                  model_time_len=model_time_len, address=l_path, nolimit_tag=nolimit_tag, return_idx=return_idx,freq=freq)
    if return_1day_label:
        y_1day, _, _, _, _, _ = load_5min_data(get_pre_trade_date(start_date), end_date, factor_list=[f'future_8_bar'], code_list=code_list,
                                               model_time_len=model_time_len, address=l_path, nolimit_tag=nolimit_tag, return_idx=return_idx,freq=freq)
        return X, y_self_define[0, :, :], nolimit, idx_date, idx_code, idx_time, y_1day, y
    return X, y_self_define[0, :, :], nolimit, idx_date, idx_code, idx_time


def load_fix_mv(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                address='/data/group/800319/HFfactor/RealTimeFixRollRobust/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/data/idx_date.npy' % address)
    idx_code = np.load('%s/data/idx_code.npy' % address)

    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1

    if return_idx:
        idx_date = idx_date[choose]
        idx_code = idx_code[choose]

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    mean = np.empty((len(factor_list), len(choose)), dtype=np.float64)
    std = np.empty((len(factor_list), len(choose)), dtype=np.float64)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/mean/{f}.npy', dtype='float64', mode='r',
                       shape=shape, offset=starts * 8 + 128)
        mean[j] = fp[choose]
        del fp

        fp = np.memmap(f'{address}/std/{f}.npy', dtype='float64', mode='r',
                       shape=shape, offset=starts * 8 + 128)
        std[j] = fp[choose]
        del fp

    if return_idx:
        return mean, std, idx_date, idx_code
    else:
        return mean, std

def feature_engineering(X, y, nolimit, *args, limit=0.2, model_time_len=1, freq=7):

    if model_time_len > 1:
        X = np.lib.stride_tricks.as_strided(X, shape=(X.shape[0], X.shape[1], freq, X.shape[2] - freq + 1),
                                            strides=(X.strides[0], X.strides[1], X.strides[2], X.strides[2]))
        X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], X.shape[3]).transpose(1, 2, 0)
        new_arg = []
        for arg in args:
            arg = np.lib.stride_tricks.as_strided(arg, (arg.shape[0], freq, arg.shape[1]-freq+1), (arg.strides[0],
                                                                         arg.strides[1], arg.strides[1]))
            new_arg.append(arg)
        args = new_arg
    else:
        X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], model_time_len).transpose(1, 2, 0)

    y = y.flatten()
    nolimit = nolimit.flatten()
    valid = ((X == 0).sum(axis=2) < limit * X.shape[2]).all(axis=1) & np.isfinite(y) & nolimit

    valid_samples = valid.sum()
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
        valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))

    X = X[valid]
    y = y[valid]
    if model_time_len>1:
        dic = {}
        for arg in range(len(args)):
            dic[arg] = args[arg].reshape((args[arg].shape[0]*args[arg].shape[1],)+args[arg].shape[2:])[valid]
    else:
        dic = {}
        for arg in range(len(args)):
            dic[arg] = args[arg].flatten()[valid]

    if model_time_len == 1:
        X = X[:, 0]

    return (X, y) + tuple(dic.values())


def load_fixes_data(start_date=20140801, end_date=20140901, factor_list=None,
                    code_list=None, return_idx=True, model_time_len=1, freq=7,
                    address_list=None):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address_list[0])
    idx_code = np.load('%s/idx_code.npy' % address_list[0])
    idx_time = np.load('%s/idx_time.npy' % address_list[0])

    time_len = idx_time.shape[0]

    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1

    if return_idx:
        idx_date = idx_date[choose, None].repeat(freq + model_time_len - 1, axis=1)
        idx_code = idx_code[choose, None].repeat(freq + model_time_len - 1, axis=1)
        idx_time = idx_time[None, 1 - freq - model_time_len:].repeat(choose.sum(), axis=0)

    fp = np.memmap(f'{address_list[0]}/future.npy', dtype='float32', mode='r', offset=128)
    real_y_shape = fp.shape[0] // freq - starts
    del fp
    real_y_shape = 0 if real_y_shape < 0 else (real_y_shape if real_y_shape < shape else shape)
    real_y_choose = (
            np.arange(choose[:starts + real_y_shape].shape[0])[choose[:starts + real_y_shape]] - starts).tolist()
    real_y_choose = slice(None) if len(real_y_choose) == real_y_shape else real_y_choose

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    X = np.empty((len(factor_list), len(choose), freq + model_time_len - 1), dtype=np.float32)
    y = np.empty((len(choose), freq), dtype=np.float32)
    nolimit = np.empty((len(choose), freq), dtype=np.bool)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        for address in address_list:
            try:
                fp = np.memmap(f'{address}/{f}.npy', dtype='float32', mode='r',
                               shape=(shape, time_len), offset=starts * time_len * 4 + 128)
            except FileNotFoundError:
                continue
            else:
                break
        X[j] = fp[choose, 1 - freq - model_time_len:]
        del fp

    if not real_y_shape:
        y[:] = np.nan
        nolimit[:] = False
    else:
        fp = np.memmap(f'{address_list[0]}/future.npy', dtype='float32', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq * 4 + 128)
        y[:real_y_shape] = fp[real_y_choose, :]
        y[real_y_shape:] = np.nan

        fp = np.memmap(f'{address_list[0]}/nolimit.npy', dtype='bool', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq + 128)
        nolimit[:real_y_shape] = fp[real_y_choose, :]
        nolimit[real_y_shape:] = False

    if return_idx:
        return X, y, nolimit, idx_date, idx_code, idx_time
    else:
        return X, y, nolimit


def infer_stock_pool(idx_date, idx_code, arr=None):
    date_list, date_i = np.unique(idx_date, return_inverse=True)
    code_list, code_i = np.unique(idx_code, return_inverse=True)
    date_list = date_list.tolist()
    code_list = code_list.tolist()
    stock_pool = np.full((date_i[-1] + 1) * (code_i[-1] + 1), False)
    date_code_i = date_i * (code_i[-1] + 1) + code_i
    stock_pool[date_code_i] = True
    stock_pool = stock_pool.reshape(date_i[-1] + 1, code_i[-1] + 1)
    if arr is not None:
        factor = np.full((date_i[-1] + 1) * (code_i[-1] + 1), np.nan, dtype=arr.dtype)
        factor[date_code_i] = arr
        factor = factor.reshape(date_i[-1] + 1, code_i[-1] + 1)
        return stock_pool, date_list, code_list, factor
    else:
        return stock_pool, date_list, code_list


def load_dataset_from_multiple_add(start, end, factor_lists, addresses, tail_no_future=False):
    print(addresses)
    idx_date, idx_time, idx_code, nolimit, y = None, None, None, None, None
    col = []
    X = []
    for idx_add, add, factor_list in zip(list(range(len(addresses))), addresses, factor_lists):
        col += [f'{x}_{idx_add}' for x in factor_list]
        X1, y1, nolimit1, idx_date1, idx_code1, idx_time1 = load_fix_data(start, end, factor_list, address=add)
        if idx_date is None:
            nolimit, idx_date, idx_time, idx_code, y = nolimit1.copy(), idx_date1.copy(), idx_time1.copy(), idx_code1.copy(), y1.copy()
        else:
            if (idx_date != idx_date1).sum() or (idx_time != idx_time1).sum() or (idx_code != idx_code1).sum():
                raise Exception(f'Nonidentical idx of {start} {end} {add}')
            if (nolimit != nolimit1).sum():
                raise Exception(f'Nonidentical nolimit flag of {start} {end} {add}')
            close = np.isclose(y, y1)
            both_nan = np.isnan(y) & np.isnan(y1)
            close[both_nan] = True
            if (~close).sum():
                raise Exception(f'Nonidentical label of {start} {end} {add}')
        X.append(X1)
    X = np.concatenate(tuple(X), axis=0)
    if tail_no_future:
        print('Newest day -------------------------')
        nolimit[np.isnan(y)] = True
        y[np.isnan(y)] = 0
    X, y, idx_date, idx_time, idx_code = feature_engineering(X, y, nolimit, idx_date, idx_time, idx_code)
    index = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_code, idx_time)))

    X = pd.DataFrame(X, columns=col, index=index)
    y = pd.DataFrame({'actual_label': y}, index=index)
    return X, y


def load_dataset_from_multiple_add_selfdefine_label(start, end, factor_lists, addresses, tail_no_future=False, label_path=None, return_1day_label=False):
    print(addresses)
    idx_date, idx_time, idx_code, nolimit, y = None, None, None, None, None
    col = []
    X = []
    for idx_add, add, factor_list in zip(list(range(len(addresses))), addresses, factor_lists):
        col += [f'{x}_{idx_add}' for x in factor_list]
        X1, y1, nolimit1, idx_date1, idx_code1, idx_time1, y_1day = load_fix_data_selfdefined_label(start, end, factor_list,
                                                                                                    address=add, label_path=label_path, return_1day_label=return_1day_label)
        if idx_date is None:
            nolimit, idx_date, idx_time, idx_code, y = nolimit1.copy(), idx_date1.copy(), idx_time1.copy(), idx_code1.copy(), y1.copy()
        else:
            if (idx_date != idx_date1).sum() or (idx_time != idx_time1).sum() or (idx_code != idx_code1).sum():
                raise Exception(f'Nonidentical idx of {start} {end} {add}')
            if (nolimit != nolimit1).sum():
                raise Exception(f'Nonidentical nolimit flag of {start} {end} {add}')
            close = np.isclose(y, y1)
            both_nan = np.isnan(y) & np.isnan(y1)
            close[both_nan] = True
            if (~close).sum():
                raise Exception(f'Nonidentical label of {start} {end} {add}')
        X.append(X1)
    X = np.concatenate(tuple(X), axis=0)
    if tail_no_future:
        print('Newest day -------------------------')
        y[np.isnan(y) & (idx_date == end)] = 0
        nolimit[(y == 0) & (idx_date == end)] = True

    X, y, idx_date, idx_time, idx_code, y_1day = feature_engineering(X, y, nolimit, idx_date, idx_time, idx_code, y_1day)
    index = pd.MultiIndex.from_tuples(list(zip(idx_date, idx_time, idx_code)))

    X = pd.DataFrame(X, columns=col, index=index)
    y = pd.DataFrame({'actual_label': y, '1_day_label': y_1day}, index=index)
    return X, y


def infer_nolimit_pool(idx_date, idx_code, idx_time, arr=None):
    date_list, date_i = np.unique(idx_date, return_inverse=True)
    code_list, code_i = np.unique(idx_code, return_inverse=True)
    time_list, time_i = np.unique(idx_time, return_inverse=True)
    date_list = date_list.tolist()
    code_list = code_list.tolist()
    time_list = time_list.tolist()
    import traceback
    try:
        nolimit_pool = np.full((date_i.max() + 1) * (code_i.max() + 1) * (time_i.max() + 1), False)
    except:
        print(1)
        e = traceback.format_exc()
        raise Exception(e)
    dct_i = date_i * (code_i.max() + 1) * (time_i.max() + 1) + code_i * (time_i.max() + 1) + time_i
    nolimit_pool[dct_i] = True
    nolimit_pool = nolimit_pool.reshape(date_i.max() + 1, code_i.max() + 1, time_i.max() + 1)
    if arr is not None:
        factor = np.full((date_i.max() + 1) * (code_i.max() + 1) * (time_i.max() + 1), np.nan, dtype=arr.dtype)
        factor[dct_i] = arr
        factor = factor.reshape(date_i.max() + 1, code_i.max() + 1, time_i.max() + 1)
        return nolimit_pool, date_list, code_list, time_list, factor
    else:
        return nolimit_pool, date_list, code_list, time_list


def loadFixTensorize(start, end, factor_list, limit=0.2, nolimit_type='df', return_type='dict',
                     address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/', swap_head_tail_axis=True):
    if not factor_list:
        return {}
    X, y, nolimit, idx_date, idx_code, idx_time = load_fix_data(start_date=start, end_date=end, factor_list=factor_list, address=address)
    X, y, idx_date, idx_code, idx_time = feature_engineering(X, y, nolimit, idx_date, idx_code, idx_time, limit=limit)

    def transfer(arr, date_list, time_list, code_list):

        arr = arr.swapaxes(1, 2)
        if nolimit_type == 'df':
            arr = pd.DataFrame(arr.reshape(len(date_list) * len(time_list), len(code_list)),
                               index=pd.MultiIndex.from_tuples(list(itertools.product(date_list, time_list))),
                               columns=code_list)
        elif nolimit_type == '2d_arr':
            arr = arr.reshape(len(date_list) * len(time_list), len(code_list))
        else:
            pass
        return arr

    args = None
    if return_type == 'dict':
        res = {}
        for idx, factor_name in enumerate(factor_list):
            _nolimit_pool, _date_list, _code_list, _time_list, _arr = infer_nolimit_pool(idx_date, idx_code, idx_time, X[:, idx])
            res[factor_name] = transfer(_arr, _date_list, _time_list, _code_list)
    elif return_type == 'multi_dim_arr':
        res = []
        for idx, factor_name in enumerate(factor_list):
            _nolimit_pool, _date_list, _code_list, _time_list, _arr = infer_nolimit_pool(idx_date, idx_code, idx_time, X[:, idx])
            temp_factor = transfer(_arr, _date_list, _time_list, _code_list)
            res.append(temp_factor[None, :])
        res = np.concatenate(res, axis=0)
    else:
        raise Exception('Wrong return type')
    _nolimit_pool, _date_list, _code_list, _time_list, label = infer_nolimit_pool(idx_date, idx_code, idx_time, y)
    label = transfer(label, _date_list, _time_list, _code_list)
    nolimit_pool = transfer(_nolimit_pool, _date_list, _time_list, _code_list)
    if return_type == 'dict':
        return res, label, nolimit_pool, _date_list, _time_list, _code_list
    if swap_head_tail_axis:
        return res.swapaxes(-1, 0), label.swapaxes(-1, 0), nolimit_pool.swapaxes(-1, 0), _date_list, _time_list, _code_list
    else:
        return res, label, nolimit_pool, _date_list, _time_list, _code_list

# factor_list = ['TwapSkewToVwap', 'Smartmoney_amt_ms05_05_rolling1', 'HF_VolumeAmtSkewRatio']
# fea,label,pool_mask, date_list, time_list, code_list = load_fix_df(20140801, 20140901,factor_list,limit=0.2,nolimit_type='2d_arr',return_type='multi_dim_arr')

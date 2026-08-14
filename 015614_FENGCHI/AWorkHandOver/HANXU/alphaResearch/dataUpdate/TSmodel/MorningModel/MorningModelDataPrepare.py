import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_daily_1factor
import pandas as pd
import numpy as np
import time
import os
import re
import gc


def morning_factor_prepare(factor_list, start_date, end_date=0, return_idx=True,
                           code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    factor_direction = factor_list['direction'].values.astype(np.int32)
    factor_list = factor_list.index.to_list()
    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose] * factor_direction[j]
        del fp

    X = X.T

    if return_idx:
        return X, idx_date, idx_code
    else:
        return X


def morning_future_prepare(start_date, end_date=0, future_type=None, future_std=None,
                           address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date
    idx_date = idx_date[choose]
    idx_code = idx_code[choose]
    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    y = np.empty(len(choose), dtype=np.float32)

    fp = np.memmap(f'{address}/{future_type}/{future_std}.npy', dtype='float32',
                   mode='r', shape=shape, offset=offset)
    y[:] = fp[choose]
    return idx_date, idx_code, y


def morning_future_prepare2(start_date, end_date=0, future_type=None, future_std=None, return_idx=True,
                            code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    ry = np.empty((len(future_type), len(choose)), dtype=np.float32)
    y = np.empty((len(future_type), len(choose)), dtype=np.float32)

    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        ry[j] = fp[choose]
        del fp
    ry = ry.mean(axis=0)

    if future_std != 'future':
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address}/{f}/{future_std}.npy', dtype='float32',
                           mode='r', shape=shape, offset=offset)
            y[j] = fp[choose]
            del fp
        y = y.mean(axis=0)
    else:
        y = ry.copy()

    gc.collect()

    if return_idx:
        return y, ry, idx_date, idx_code
    else:
        return y, ry


def morning_data_prepare(factor_list, start_date, end_date=0, future_type=None, future_std=None, return_idx=True,
                         code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    ry = np.empty(len(choose), dtype=np.float32)
    if future_std != 'future':
        y = np.empty(len(choose), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    factor_direction = factor_list['direction'].values.astype(np.int32)
    factor_list = factor_list.index.to_list()
    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose] * factor_direction[j]
        del fp

    fp = np.memmap(f'{address}/{future_type}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
    ry[:] = fp[choose]
    del fp

    if future_std != 'future':
        fp = np.memmap(f'{address}/{future_type}/{future_std}.npy', dtype='float32',
                       mode='r', shape=shape, offset=offset)
        y[:] = fp[choose]
        del fp
    else:
        y = ry.copy()

    X = X.T

    if return_idx:
        return X, y, ry, idx_date, idx_code
    else:
        return X, y, ry


def morning_data_prepare2(factor_list, start_date, end_date=0, future_type=None, future_std=None, return_idx=True,
                          code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    ry = np.empty((len(future_type), len(choose)), dtype=np.float32)
    y = np.empty((len(future_type), len(choose)), dtype=np.float32)

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    factor_direction = factor_list['direction'].values.astype(np.int32)
    factor_list = factor_list.index.to_list()
    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose] * factor_direction[j]
        del fp

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        ry[j] = fp[choose]
        del fp
    ry = ry.mean(axis=0)

    if future_std != 'future':
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address}/{f}/{future_std}.npy', dtype='float32',
                           mode='r', shape=shape, offset=offset)
            y[j] = fp[choose]
            del fp
        y = y.mean(axis=0)
    else:
        y = ry.copy()

    X = X.T
    gc.collect()

    if return_idx:
        return X, y, ry, idx_date, idx_code
    else:
        return X, y, ry


def morning_data_prepare7(factor_list, start_date, end_date=0, future_type=None, future_std=None, return_idx=True,
                          code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    ry = np.empty((len(future_type), len(choose)), dtype=np.float32)
    y = np.empty((len(future_type), len(choose)), dtype=np.float32)

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose]
        del fp

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        ry[j] = fp[choose]
        del fp
    ry = ry.mean(axis=0)

    if future_std != 'future':
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address}/{f}/{future_std}.npy', dtype='float32',
                           mode='r', shape=shape, offset=offset)
            y[j] = fp[choose]
            del fp
        y = y.mean(axis=0)
    else:
        y = ry.copy()

    X = X.T
    gc.collect()

    if return_idx:
        return X, y, ry, idx_date, idx_code
    else:
        return X, y, ry


def morning_data_prepare7(factor_list, start_date, end_date=0, future_type=None, future_std=None, return_idx=True,
                          code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    ry = np.empty((len(future_type), len(choose)), dtype=np.float32)
    y = np.empty((len(future_type), len(choose)), dtype=np.float32)

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose]
        del fp

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        ry[j] = fp[choose]
        del fp
    ry = ry.mean(axis=0)

    if future_std != 'future':
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address}/{f}/{future_std}.npy', dtype='float32',
                           mode='r', shape=shape, offset=offset)
            y[j] = fp[choose]
            del fp
        y = y.mean(axis=0)
    else:
        y = ry.copy()

    X = X.T
    gc.collect()

    if return_idx:
        return X, y, ry, idx_date, idx_code
    else:
        return X, y, ry

def morning_factor_prepare7(factor_list, start_date, end_date=0, return_idx=True,
                          code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose]
        del fp

    X = X.T
    gc.collect()

    if return_idx:
        return X, idx_date, idx_code
    else:
        return X

def morning_data_fix_end_prepare(factor_list, start_date, end_date=0, future_type=None, future_std=None):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)
    address1 = '/data/group/800442/800319/HFfactor/MorningFactorFixEnd/data/'
    address2 = '/data/group/800442/800319/HFfactor/MorningFactor/data/'
    idx_date = np.load('%s/idx_date.npy' % address1)
    idx_code = np.load('%s/idx_code.npy' % address1)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address1)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    idx_date = idx_date[choose]
    idx_code = idx_code[choose]
    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    ry = np.empty((len(future_type), len(choose)), dtype=np.float32)
    y = np.empty((len(future_type), len(choose)), dtype=np.float32)

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        real_name = f.split('_', 1)[1]
        if re.match('^Fix1[0134][03]0_', real_name):
            fp = np.memmap(f'{address1}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        else:
            fp = np.memmap(f'{address2}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose]
        del fp

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address1}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        ry[j] = fp[choose]
        del fp
    ry = ry.mean(axis=0)

    if future_std != 'future':
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address1}/{f}/{future_std}.npy', dtype='float32',
                           mode='r', shape=shape, offset=offset)
            y[j] = fp[choose]
            del fp
        y = y.mean(axis=0)
    else:
        y = ry.copy()

    X = X.T
    gc.collect()
    return X, y, ry, idx_date, idx_code


def morning_data_prepare8(factor_list1, factor_list2, start_date, end_date=0, future_type=None, future_std=None,
                          return_idx=True, code_list=None,
                          address1='/data/group/800442/800319/HFfactor/MorningFactor/data/',
                          address2='/arch1/user/015836/LimitUpStrategy2/restore/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address1)
    idx_code = np.load('%s/idx_code.npy' % address1)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address1)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    ry = np.empty((len(future_type), len(choose)), dtype=np.float32)
    y = np.empty((len(future_type), len(choose)), dtype=np.float32)

    X = np.empty((len(factor_list1) + len(factor_list2), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list1):
        fp = np.memmap(f'{address1}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose]
        del fp

    for j, f in enumerate(factor_list2):
        fp = np.memmap(f'{address2}/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[len(factor_list1) + j] = fp[choose]
        del fp

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address1}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        ry[j] = fp[choose]
        del fp
    ry = ry.mean(axis=0)

    if future_std != 'future':
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address1}/{f}/{future_std}.npy', dtype='float32',
                           mode='r', shape=shape, offset=offset)
            y[j] = fp[choose]
            del fp
        y = y.mean(axis=0)
    else:
        y = ry.copy()

    X = X.T
    gc.collect()

    if return_idx:
        return X, y, ry, idx_date, idx_code
    else:
        return X, y, ry

def morning_data_prepare4(factor_list, start_date, end_date=0, future_type=None, return_idx=True,
                          code_list=None, address='/data/group/800442/800319/HFfactor/MorningTimingFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    y = np.empty((len(future_type), len(choose)), dtype=np.float32)
    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose]
        del fp

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        y[j] = fp[choose]
        del fp
    y = y.mean(axis=0)
    X = X.T
    gc.collect()

    if return_idx:
        return X, y, idx_date, idx_code
    else:
        return X, y

def morning_data_prepare5(factor_list, start_date, end_date=0, future_type=None, future_std='future', return_idx=True,
                          code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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


    y = np.empty(len(choose), dtype=np.float32)
    ry = np.empty(len(choose), dtype=np.float32)
    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose]
        del fp

    fp = np.memmap(f'{address}/{future_type}/{future_std}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
    y[:] = fp[choose]
    del fp

    fp = np.memmap(f'{address}/{future_type}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
    ry[:] = fp[choose]
    del fp

    X = X.T
    gc.collect()

    if return_idx:
        return X, y, ry, idx_date, idx_code
    else:
        return X, y, ry

def morning_data_prepare6(factor_list, start_date, end_date=0, future_type=None, future_std=None, return_idx=True,
                          code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    y = np.empty(len(choose), dtype=np.float32)

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    factor_direction = factor_list['direction'].values.astype(np.int32)
    factor_list = factor_list.index.to_list()
    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose] * factor_direction[j]
        del fp

    fp = np.memmap(f'{address}/{future_type}/{future_std}.npy', dtype='float32',
                   mode='r', shape=shape, offset=offset)
    y[:] = fp[choose]
    del fp
    X = X.T
    gc.collect()

    if return_idx:
        return X, y, idx_date, idx_code
    else:
        return X, y

def future_data_prepare4(start_date, end_date, future_type=None, return_idx=True,
                         code_list=None, address='/data/group/800442/800319/HFfactor/MorningTimingFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    y = np.empty((len(future_type), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        y[j] = fp[choose]
        del fp
    y = y.mean(axis=0)
    gc.collect()

    if return_idx:
        return y, idx_date, idx_code
    else:
        return y

def factor_data_prepare4(factor_list, start_date, end_date=0, return_idx=True,
                         code_list=None, address='/data/group/800442/800319/HFfactor/MorningTimingFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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
    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose]
        del fp

    X = X.T
    gc.collect()

    if return_idx:
        return X, idx_date, idx_code
    else:
        return X


def morning_data_prepare3(factor_list1, factor_list2, start_date, end_date=0, future_type=None, future_std=None,
                          return_idx=True, code_list=None,
                          address1='/data/group/800442/800319/HFfactor/MorningFactor/data/',
                          address2='/arch1/group/800442/800319/AAcross/model_factor_daily/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address1)
    idx_code = np.load('%s/idx_code.npy' % address1)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address1)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
    future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]

    ry = np.empty((len(future_type), len(choose)), dtype=np.float32)
    y = np.empty((len(future_type), len(choose)), dtype=np.float32)

    X = np.empty((len(factor_list1) + len(factor_list2), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    factor_direction = factor_list1['direction'].values.astype(np.int32)
    factor_list1 = factor_list1.index.to_list()
    for j, f in enumerate(factor_list1):
        fp = np.memmap(f'{address1}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose] * factor_direction[j]
        del fp

    for j, f in enumerate(factor_list2):
        fp = np.memmap(f'{address2}/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[len(factor_list1) + j] = fp[choose]
        del fp

    for j, f in enumerate(future_type):
        fp = np.memmap(f'{address1}/{f}/future.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        ry[j] = fp[choose]
        del fp
    ry = ry.mean(axis=0)

    if future_std != 'future':
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address1}/{f}/{future_std}.npy', dtype='float32',
                           mode='r', shape=shape, offset=offset)
            y[j] = fp[choose]
            del fp
        y = y.mean(axis=0)
    else:
        y = ry.copy()

    X = X.T
    gc.collect()

    if return_idx:
        return X, y, ry, idx_date, idx_code
    else:
        return X, y, ry


def morning_factor_prepare2(factor_list, start_date, end_date=0, return_idx=True,
                            code_list=None, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    drop_offset = pd.read_pickle('%s/drop_offset.pkl' % address)
    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts
    offset = starts * 4 + 256 - drop_offset

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

    X = np.empty((len(factor_list), len(choose)), dtype=np.float32)
    choose = slice(None) if len(choose) == shape else choose

    factor_direction = factor_list['direction'].values.astype(np.int32)
    factor_list = factor_list.index.to_list()
    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/factor/{f}.npy', dtype='float32', mode='r', shape=shape, offset=offset)
        X[j] = fp[choose] * factor_direction[j]
        del fp

    X = X.T
    gc.collect()

    if return_idx:
        return X, idx_date, idx_code
    else:
        return X


def prepare_size_rank(start_date, end_date=0, address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)
    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date
    idx_date = idx_date[choose]
    idx_code = idx_code[choose]

    date_list, date_i = np.unique(idx_date, return_inverse=True)
    code_list, code_i = np.unique(idx_code, return_inverse=True)
    date_list = [int(x) for x in date_list]
    code_list = [int(x) for x in code_list]
    stock_pool = np.full((date_i[-1] + 1) * (code_i[-1] + 1), False)
    date_code_i = date_i * (code_i[-1] + 1) + code_i
    stock_pool[date_code_i] = True
    stock_pool = stock_pool.reshape(date_i[-1] + 1, code_i[-1] + 1)

    size = get_daily_1factor('mkt_cap_ard', date_list, code_list)
    size[~ stock_pool] = np.nan
    return size.mean().sort_values(ascending=False).index.to_list()


def factor_engineering(X, *args):
    valid = (np.isfinite(X).sum(axis=1) > 0.8 * X.shape[1])

    valid_samples = valid.sum()
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
        valid_samples, X.shape[0], round(valid_samples / X.shape[0] * 100, 1)))

    X = X[valid]
    X[~ np.isfinite(X)] = 0

    dic = {}
    for arg in range(len(args)):
        dic[arg] = args[arg][valid]

    return (X,) + tuple(dic.values())


def feature_engineering(X, y, *args):
    valid = (np.isfinite(X).sum(axis=1) > 0.8 * X.shape[1]) & np.isfinite(y)

    valid_samples = valid.sum()
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
        valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))

    X = X[valid]
    y = y[valid]
    X[~ np.isfinite(X)] = 0

    dic = {}
    for arg in range(len(args)):
        dic[arg] = args[arg][valid]

    return (X, y) + tuple(dic.values())


def split_train_predict(start_date, end_date, train_days=380, predict_days=10, future_days_max=1, roll_days=1):
    date_list = get_date_range(start_date, end_date)
    predict_ends = sorted(date_list[-1: train_days + predict_days +
                                        future_days_max + roll_days - 3: -predict_days])
    predict_starts = [date_list[date_list.index(x) - predict_days + 1] for x in predict_ends]
    train_ends = [date_list[date_list.index(x) - future_days_max - 1] for x in predict_starts]
    train_starts = [date_list[date_list.index(x) - train_days + 1] for x in train_ends]
    train_roll_starts = [date_list[date_list.index(x) - train_days - roll_days + 2] for x in train_ends]
    model_index = list(range(len(predict_ends)))
    model_date_list = {k: (train_roll_starts[k], train_starts[k], train_ends[k],
                           predict_starts[k], predict_ends[k]) for k in model_index}

    return model_date_list


def split_train_test(start_date, end_date, test_date_idx):
    test_dates = [get_pre_trade_date(end_date, ~ x) for x in sorted(test_date_idx)]
    date_list = get_date_range(start_date, end_date)
    train_dates = sorted(list(set(date_list) - set(test_dates)))
    return train_dates, test_dates


def select_factor_list(train_end, factor_num=400, prefix='TS',
                       statistics_address='/data/group/800442/800319/HFfactor/MorningFactor/statistics/ic/'):
    files = sorted([int(x[len(prefix):].split('.')[0]) for x in os.listdir(statistics_address)
                    if x[:len(prefix)] == prefix])
    file = [x for x in files if train_end // 100 - 200000 > x]
    file = file[-1] if file else files[0]
    factor_list = pd.read_excel('%s/%s%s.xlsx' % (statistics_address, prefix, file), index_col=0)
    factor_list = factor_list[['score', 'direction']].sort_values('score', ascending=False).head(factor_num)
    print('train_end', train_end, 'factor_list', file, 'factor_num', len(factor_list))
    return factor_list


def select_factor_list2(train_end, factor_num=400, prefix='TS', corr_ignore=False,
                        statistics_address='/data/group/800442/800319/HFfactor/MorningFactor/statistics/ic/'):
    files = sorted([int(x[len(prefix):].split('.')[0]) for x in os.listdir(statistics_address)
                    if x[:len(prefix)] == prefix])
    file = [x for x in files if train_end // 100 - 200000 > x]
    file = file[-1] if file else files[0]
    factor_list = pd.read_excel('%s/%s%s.xlsx' % (statistics_address, prefix, file), index_col=0)
    if not corr_ignore:
        factor_list = factor_list[factor_list['corr_pass']]
    factor_list = factor_list.sort_values('score', ascending=False).head(factor_num)
    print('train_end', train_end, 'factor_list', file, 'factor_num', len(factor_list))
    return factor_list

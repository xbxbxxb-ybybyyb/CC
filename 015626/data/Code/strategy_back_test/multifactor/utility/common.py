from __future__ import print_function  # cython issue
import pandas as pd
import numpy as np
from collections.abc import Iterable
import random
import re
from pathlib import Path
import json
import dill
import os
import sys
from multiprocessing import Pool
import multiprocessing
import multiprocessing.pool
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import multifactor.utility.dt as tdt
from multifactor.utility.decorated import *
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.IO.naming_config as ionc
import datetime as dt
import logging
import warnings
from collections.abc import Sequence
import copy
from decimal import Decimal, ROUND_HALF_UP
from statsmodels.stats.weightstats import DescrStatsW
import statsmodels.api as smapi
import itertools
import threading
from scipy.special import expit
import concurrent.futures
import scipy.optimize as optimize
import scipy.stats
import functools
import zipfile
import shutil
from tqdm import tqdm


def error_checker(left, right, threshold=0.0001, sample_num=5):
    left_ps = left.dropna()
    right_ps = right.dropna()
    # Error rate check
    mutual_idx = left_ps.index.intersection(right_ps.index)
    if len(mutual_idx) == 0:
        raise AssertionError('No Mutual Data')
    # Data look back effect removal
    left_mut_ps = left_ps.reindex(mutual_idx, fill_value=0)
    right_mut_ps = right_ps.reindex(mutual_idx, fill_value=0)
    deviation_ps = ((left_mut_ps - right_mut_ps) / (left_mut_ps + right_mut_ps) * 2).abs()
    error_ps = deviation_ps.loc[deviation_ps >= threshold]
    error_rate = len(error_ps) / len(mutual_idx)
    max_error = error_ps.max()
    # Fill rate check
    if len(mutual_idx.get_level_values(level=0).hour.unique()) == 1:
        common_dates = list(mutual_idx.get_level_values(level=0).unique())
    else:
        common_dates = list(np.unique(mutual_idx.get_level_values(level=0).date))
    fill_rate_lst = []
    # Downsampling needed to save time
    common_num = len(common_dates)
    if common_num <= sample_num:
        sample_lst = range(0, common_num)
    else:
        sample_lst = list(set([np.random.randint(0, common_num) for i in range(sample_num)]))
    for item in sample_lst:
        sample_date = common_dates[item].strftime('%Y%m%d')
        fill_rate_lst.append(len(left_ps.loc[sample_date]) / len(right_ps.loc[sample_date]))
    fill_rate_ratio = np.mean(fill_rate_lst)
    return error_rate, max_error, fill_rate_ratio


def ratio_shrinkage(x, target_ratio=10, target_sum=None):
    assert np.any([isinstance(x, item) for item in [list, np.ndarray, pd.Series]])
    _x = pd.Series(np.array(x).ravel())
    _x = _x - _x.min() + 1
    if _x.max() != 1:
        _x = np.power(_x, np.log(target_ratio) / np.log(_x.max()))
    else:
        warnings.warn('constant input detected')
    if target_sum is None:
        target_sum = len(_x)
    _x = np.array(_x)
    if isinstance(x, list):
        _x = list(_x)
    elif isinstance(x, pd.Series):
        _x = pd.Series(_x, index=x.index)
    return vec_normalize(_x, norm=target_sum)


def np_valid(array, fillna=False):
    # Retrieve valid elements in array
    x = np.array(array) if not isinstance(array, np.ndarray) else array
    y = np.ma.masked_invalid(x)
    if fillna:
        return y.filled(np.nan)
    else:
        return y.data[~y.mask]


def vec_normalize(vec, norm=1):
    _vec = np.fabs(np.array(vec)).reshape(-1)
    _sum = _vec[~np.isnan(_vec)].sum()
    if _sum != 1 and _sum != 0:
        _vec = _vec * norm / _sum
        _vec = [i * abs(j) / j if j !=0 else 0 for i, j in zip(_vec, vec)]
        if type(vec) == np.ndarray:
            return np.array(_vec)
        elif type(vec) == list:
            return _vec
        elif type(vec) == pd.Series:
            _vec = pd.Series(_vec, index=vec.index)
            _vec.name = vec.name
            return _vec
        else:
            raise AssertionError
    else:
        return vec


def diller(file_name, payload=None):
    if payload is None:
        with open(file_name, 'rb') as fin:
            return dill.load(fin)
    else:
        with open(file_name, 'wb') as fout:
            dill.dump(payload, fout, protocol=4)


def encrypter(msg, secret, aes_mode=AES.MODE_CFB, initial_vec=None):
    assert isinstance(msg, str) or isinstance(msg, bytes)
    assert isinstance(secret, str)
    # Prepare initial vector
    if initial_vec is None:
        initial_vec = Random.new().read(AES.block_size)
    # Encrypt message
    hasher = hashlib.sha256()
    hasher.update(secret.encode('utf-8'))
    encryption_cipher = AES.new(hasher.digest(), aes_mode, initial_vec)
    if isinstance(msg, str):
        return initial_vec + encryption_cipher.encrypt(msg.encode('utf-8'))
    elif isinstance(msg, bytes):
        return initial_vec + encryption_cipher.encrypt(msg)
    else:
        raise AssertionError


def decrypter(msg, secret, aes_mode=AES.MODE_CFB, dtype=str):
    assert isinstance(msg, str) or isinstance(msg, bytes)
    assert isinstance(secret, str)
    # Decrypt message
    hasher = hashlib.sha256()
    hasher.update(secret.encode('utf-8'))
    decryption_cipher = AES.new(hasher.digest(), aes_mode, msg[:AES.block_size])
    if dtype == str:
        return decryption_cipher.decrypt(msg[AES.block_size:]).decode('utf-8')
    elif dtype == bytes:
        return decryption_cipher.decrypt(msg[AES.block_size:])
    else:
        raise AssertionError


def get_default_secret(aes_mode=AES.MODE_CFB):
    dt = pd.Timestamp.now().date().strftime('%Y%m%d')
    return f'{dt}-MAAL-{aes_mode}'


def get_encrypted_file_name(file_name, secret=None, aes_mode=AES.MODE_CFB):
    if secret is None:
        secret = get_default_secret(aes_mode)
    initial_vec = bytes((secret * AES.block_size).encode('utf-8'))[:AES.block_size]
    encrypted_file_name = encrypter(os.path.basename(file_name), secret,
                                   initial_vec=initial_vec).hex()
    return encrypted_file_name + '.bin'


def get_decrypted_file_name(file_name, secret=None, aes_mode=AES.MODE_CFB):
    if secret is None:
        secret = get_default_secret(aes_mode)
    assert file_name[-4:] == '.bin'
    return decrypter(bytes.fromhex(os.path.basename(file_name[:-4])), secret, dtype=str)


def file_encrypter(file_name, output_path=None, secret=None, aes_mode=AES.MODE_CFB, encrypt_file_name=False):
    if secret is None:
        secret = get_default_secret(aes_mode)
    if output_path is None:
        if encrypt_file_name:
            encrypted_file_name = get_encrypted_file_name(file_name, secret, aes_mode)
            output_path = os.path.join(os.path.dirname(file_name), encrypted_file_name)
        else:
            output_path = file_name + '.bin'
    with open(file_name, 'rb') as fin:
        msg = fin.read()
    encrypted_msg = encrypter(msg, secret)
    with open(output_path, 'wb') as fout:
        fout.write(encrypted_msg)


def file_decrypter(file_name, output_path=None, secret=None, aes_mode=AES.MODE_CFB, decrypt_file_name=False):
    if secret is None:
        secret = get_default_secret(aes_mode)
    if output_path is None:
        assert file_name[-4:] == '.bin'
        if decrypt_file_name:
            decrypted_file_name = get_decrypted_file_name(file_name, secret, aes_mode)
            output_path = os.path.join(os.path.dirname(file_name), decrypted_file_name)
        else:
            output_path = file_name[:-4]
    with open(file_name, 'rb') as fin:
        msg = fin.read()
    decrypted_msg = decrypter(msg, secret, dtype=bytes)
    with open(output_path, 'wb') as fout:
        fout.write(decrypted_msg)


def chunks(l, n):
    # yield successive n-sized chunks from l
    for i in range(0, len(l), n):
        yield l[i:i+n]


def into_subchunks(x, subchunk_length, every_n=1):
    """
    Split the time series x into subwindows of length "subchunk_length", starting every "every_n".

    For example, the input data if [0, 1, 2, 3, 4, 5, 6] will be turned into a matrix

        0  1  2
        2  3  4
        4  5  6

    with the settings subchunk_length = 3 and every_n = 2
    """
    len_x = len(x)

    assert subchunk_length > 1
    assert every_n > 0

    # how often can we shift a window of size subchunk_length over the input?
    num_shifts = (len_x - subchunk_length) // every_n + 1
    shift_starts = every_n * np.arange(num_shifts)
    indices = np.arange(subchunk_length)

    indexer = np.expand_dims(indices, axis=0) + np.expand_dims(shift_starts, axis=1)
    return np.asarray(x)[indexer]


def to_timedelta(x):
    # convert datetime.time to datetime.timedelta
    assert isinstance(x, dt.time)
    return dt.datetime.combine(dt.date.min, x) - dt.datetime.min


def minute_markers(open_time=930, close_time=1500, breaks=((1130, 1300), ), step=1, buckets=None, to_datetime=True):
    if isinstance(open_time, dt.time):
        open_time = int(open_time.strftime('%H%M'))
    if isinstance(close_time, dt.time):
        close_time = int(close_time.strftime('%H%M'))
    assert isinstance(open_time, int) and isinstance(close_time, int)
    open_hours = [item for item in range(int(open_time / 100), int(close_time / 100) + 1)]
    minute_list = [i for i in range(open_time, close_time + 1, step) if (i % 100 < 60 and int(i / 100) in open_hours)]
    for break_start, break_end in breaks:
        if isinstance(break_start, dt.time):
            break_start = int(break_start.strftime('%H%M'))
        if isinstance(break_end, dt.time):
            break_end = int(break_end.strftime('%H%M'))
        assert isinstance(break_start, int) and isinstance(break_end, int)
        minute_list = [i for i in minute_list if not (i < break_end and i > break_start)]
    if buckets is not None:
        minute_list = [item[-1] for item in np.array_split(np.array(minute_list), buckets)]
    if to_datetime:
        minute_list = [dt.time(hour=int(item / 100), minute=item % 100) for item in minute_list]
    return minute_list


def quadratic_interp_weight(N, ratio=0.5, area=1):
    # given N, return weights in [1, 2, ..., N]
    # the integral of which sums to given area
    # f(0) = f(N), f(0) / f(N / 2) = ratio
    coef = np.array([[N**3 / 3, N**2 / 2,          N],
                     [N       ,        1,          0],
                     [N**2 / 4,    N / 2,  1 - ratio]])
    B = np.array([[1, 0, 0]]).T
    a, b, c = np.dot(np.linalg.inv(coef), B).ravel()
    integral = [a / 3 * i**3 + b / 2 * i**2 + c * i for i in range(0, N+1)]
    return [integral[i] - integral[i-1] for i in range(1, N+1)]


def multi_astype(pd_raw, dtype='object'):
    if type(pd_raw) not in [pd.DataFrame, pd.Series]:
        raise AssertionError
    if pd_raw.index.levels[1].dtype_str == dtype:
        return pd_raw
    y = pd_raw.reset_index()
    y.Ticker = y.Ticker.astype(dtype)
    y.set_index(['dt', 'Ticker'], append=False, inplace=True)
    y = y.sort_index(level=0)
    if type(pd_raw) == pd.Series:
        return y.iloc[:, 0]
    else:
        return y


def pd_unstack(pd_raw):
    if type(pd_raw) == pd.DataFrame:
        columns_lst = pd_raw.columns
    elif type(pd_raw) == pd.Series:
        columns_lst = []
    else:
        raise AssertionError
    if len(columns_lst) > 1:
        rtn = {}
        for item in columns_lst:
            rtn[item]= pd_raw[item].unstack()
    else:
        if type(pd_raw) == pd.Series:
            rtn = pd_raw.unstack()
        else:
            rtn = pd_raw.loc[:, columns_lst[0]].unstack()
    return rtn


def pd_stack(rtn, name='stacked'):
    # Opposite operation of pd_unstack
    if isinstance(rtn, dict):
        pd_lst = []
        for key in rtn:
            stacked = rtn[key].stack()
            stacked.name = key
            pd_lst.append(stacked)
        return pd.concat(pd_lst, axis=1)
    elif isinstance(rtn, pd.DataFrame):
        stacked = rtn.stack()
        stacked.name = name
        return stacked
    else:
        raise AssertionError


def flatten(items):
    """
    Yield items from any nested iterable
    """
    for item in items:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        else:
            yield item


def flatten_nested_lst(items):
    """
    Return [a, b, c, d] for [[a, b], [c, d]]
    """
    _res = []
    for item in items:
        if isinstance(item, list):
            _res.extend(item)
        else:
            _res.append(item)
    return _res


def rank(array, strict=True):
    if strict:
        y = np.ma.masked_invalid(pd.Series(array).rank())
    else:
        y = np.ma.masked_invalid(array) if not isinstance(array, np.ma.MaskedArray) else array
        x = y.data[~y.mask]
        temp = x.argsort()
        rtn = np.empty_like(temp)
        rtn[temp] = np.arange(len(x))
        y[~y.mask] = rtn
    return y.tolist() if not isinstance(array, np.ndarray) else y


def cov(i, j, fill_rate=0.5, normalized=False):
    # Normalized equals correlation coefficient
    i = i if isinstance(i, np.ma.MaskedArray) else np.ma.masked_invalid(i)
    j = j if isinstance(j, np.ma.MaskedArray) else np.ma.masked_invalid(j)
    union_mask = np.ma.mask_or(i.mask, j.mask, shrink=False)
    if np.count_nonzero(union_mask) / i.size >= 1 - fill_rate:
        return np.nan
    else:
        i = i.data[~union_mask]
        j = j.data[~union_mask]
        result = np.cov(i, j, bias=True)[0, 1]
        if normalized:
            return result / np.std(i) / np.std(j)
        else:
            return result


def filtered_agg(i, func, fill_rate=0.5):
    # Given np.array 1D, apply aggregation func with fill rate in consideration
    i = i if isinstance(i, np.ma.MaskedArray) else np.ma.masked_invalid(i)
    if 1 - np.count_nonzero(i.mask) / i.size >= fill_rate:
        return float(func(i.data[~i.mask]))
    else:
        return np.nan


def apply_along_row(func, array, *args, **kwargs):
    # array is 2D
    res = np.full_like(array[:, 0], np.nan, dtype=np.double)
    idx = 0
    for row in array:
        res[idx] = func(row, *args, **kwargs)
    return res


def str2num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def rolling_window(a, window):
    # Chop input array along last axis
    assert isinstance(a, np.ndarray)
    a = a.filled(np.nan) if isinstance(a, np.ma.MaskedArray) else a
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1], )
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def perturb(i, level=1):
    """
    Change the value of input while keep its sign and type
    :param i: float or int
    :param level: 0~1, untouched~(0~2*i)
    :return: perturbed value
    """
    j = abs(i)
    if type(i) == int:
        r = int(level * j)
        j = j + random.randint(-r, r)
    elif type(i) == float:
        r = level * j
        j = j + random.uniform(-r, r)
    else:
        raise AssertionError
    if i >= 0:
        return j
    else:
        return -j


def gauss_perturb(i, level=0.5, low=2, high=None):
    """
    Change the value of input while try to keep its sign and type
    :param i: float or int
    :param level: std of gauss distribution = level * i
    :param low: const parameters are usually ts days (0/1 days is meaningless)
    :return: perturbed value
    """
    j = abs(i)
    if j == 0.0:
        j = random.gauss(j, sigma=level)
    else:
        j = random.gauss(j, sigma=level * j)
    if type(i) == int:
        j = int(j)
        if low is not None:
            if abs(j) < low:
                j = low
        if high is not None:
            if abs(j) > high:
                j = high
    elif type(i) == float:
        pass
    else:
        raise AssertionError
    if i > 0:
        return abs(j)
    elif i < 0:
        return -abs(j)
    else:
        return j


def resider(x, y, method='lstsq', add_const=True, mean_only=False, r_square=False, return_sm=False, median_flag=False):
    # Two step regression
    # 1: Determine dummy columns in matrix and use them to remove mean
    # 2: Regular ols: OLS or least square to calculate residual
    # Direct OLS or least square may have problems with dummy columns with few 1s
    # Less computation and more robustness
    # x -> axis0: stocks, axis1: factors
    # median_flag: use dummy columns median instead of mean
    # useful for financial data with fat-tail distribution
    y = y.flatten()  # 1-D array
    dummy_cols = np.apply_along_axis(is_dummy, 0, x)
    d_array = x[:, dummy_cols]
    s_array = x[:, ~dummy_cols]
    r2 = np.nan
    if d_array.shape[1] != 0:
        if not median_flag:
            d_mean_array = np.array([i / j if j != 0 else 0 for i, j in
                                     zip(np.dot(d_array.T, y).flatten(), d_array.sum(axis=0))])
        else:
            d_mean_array = np.array([np.median(i[np.nonzero(i)]) for i in (d_array.T * y)])
        y = y - np.dot(d_array, d_mean_array)
    if not mean_only and s_array.shape[1] != 0:
        if method == 'lstsq':
            if add_const:
                # Prepend constant in accordance with sm.OLS
                x = np.concatenate((np.ones((s_array.shape[0], 1)), s_array), axis=1)
            else:
                x = s_array
            with np.errstate(over='raise'):
                try:
                    with HidePrints(hide_err=True):
                        coeff, residual_sum = np.linalg.lstsq(x, y, rcond=None)[0:2]
                    resid = y - np.dot(x, coeff)
                    if r_square:
                        r2 = 1 - residual_sum[0] / (y.size * y.var())
                except ArithmeticError:
                    resid = np.full_like(y, np.nan, dtype=np.double)
                    if r_square:
                        r2 = np.nan
        elif method == 'sm.OLS':
            x = s_array
            try:
                if add_const:
                    ols_problem = smapi.OLS(y, smapi.add_constant(x)).fit()
                else:
                    ols_problem = smapi.OLS(y, x).fit()
                if return_sm:
                    return ols_problem
                resid = ols_problem.resid
                if r_square:
                    r2 = ols_problem.rsquared
            except:
                if return_sm:
                    raise ValueError
                else:
                    resid = np.full_like(y, np.nan, dtype=np.double)
        else:
            raise AssertionError
    else:
        resid = y
    if return_sm:  # x contains only dummy columns
        raise ValueError
    if r_square:
        return resid, r2
    else:
        return resid


def batch_resider(x, y, *args, **kwargs):
    # deals with y of dimension more than one
    if len(y.shape) > 1:
        res = list()
        for i in range(y.shape[1]):
            res.append(resider(x, y[:, i]), *args, **kwargs)
        res = np.vstack(res).T
    else:
        res = resider(x, y, *args, **kwargs)
    return res


def is_dummy(x):
    x = np.array(x) if not isinstance(x, np.ndarray) else x
    one_num = np.count_nonzero(x == 1)
    zero_num = np.count_nonzero(x == 0)
    if one_num + zero_num == x.size:
        return True
    else:
        return False


def dic2str(dic, sep='='):
    items = []
    for key in dic:
        items.append(str(key)+sep+str(dic[key]))
    return items


def nan_agg_ufunc(x, ufunc, threshold, look_back_days):
    assert isinstance(x, np.ndarray)
    y = np.ma.masked_invalid(x)
    y = y.data[~y.mask]
    try:
        fill_rate = y.size / (x.size - look_back_days)
    except ZeroDivisionError:
        return np.nan
    if fill_rate < threshold:
        return np.nan
    else:
        return ufunc(y)


def nanstd(x, threshold=0.5, look_back_days=0):
    return nan_agg_ufunc(x, np.std, threshold=threshold, look_back_days=look_back_days)


def nanmean(x, threshold=0.5, look_back_days=0):
    return nan_agg_ufunc(x, np.mean, threshold=threshold, look_back_days=look_back_days)


def replacer(x, y, s, delimiter='%', toggle=False):
    # Replace x with y in s, except parts wrapped in delimiter
    # Vice versa for toggle
    nested_lst = re.findall(r'(%.+?%)', s)
    nested_lst.reverse()

    def nest_fill(match_obj):
        if not toggle:
            return nested_lst.pop()
        else:
            return nested_lst.pop().replace(x, y)
    w = re.sub(r'(' + delimiter + r'.+?' + delimiter + r')', '_@_', s)
    if not toggle:
        w = w.replace(x, y)
    return re.sub(r'_@_', nest_fill, w)


def tracer(key):
    path = Path.home().joinpath('multifactor.json')
    counter = read_tracer(path)
    counter = auto_add(key, counter)
    set_tracer(path, counter)


def read_tracer(path):
    Path.touch(path)
    with open(path, 'r') as fin:
        try:
            counter = json.load(fin)
        except json.JSONDecodeError:
            counter = None
    return counter


def set_tracer(path, value):
    Path.touch(path)
    with open(path, 'w') as fout:
        json.dump(value, fout)


def read_json(path):
    with open(path, 'r') as fin:
        try:
            data = json.load(fin)
        except json.JSONDecodeError:
            data = None
    return data


def dump_json(path, value):
    with open(path, 'w') as fout:
        json.dump(value, fout)


def auto_add(key, var):
    if var is None:
        var = dict()
    if key in var:
        var[key] += 1
    else:
        var[key] = 1
    return var


def link_collector(pair_lst):
    set_lst = []
    for pair in pair_lst:
        if len(set_lst) == 0:
            set_lst.append(set(pair))
        else:
            assigned = False
            for _set in set_lst:
                if np.any([i in _set for i in pair]):
                    _set.update(pair)
                    assigned = True
                    break
            if not assigned:
                set_lst.append(set(pair))
    return set_lst


def deep_link(score_mtx, threshold, score_vec=None, max_workers=None):
    # Given distance matrix, return list of sets of nearest neighbors
    # Elements are judged as neighbors with propagation: A~B, B~C -> A~C
    # Given score_vec, return discard list instead (keeping higher score)
    pair_lst = np.argwhere(score_mtx>=threshold)
    if max_workers is not None:
        max_workers = int(max_workers)
        _len = len(pair_lst)
        with Pool(processes=max_workers) as pool:
            res = pool.map(link_collector, chunks(pair_lst, int(_len/max_workers) + 1))
        set_lst = flatten_nested_lst(res)
    else:
        set_lst = link_collector(pair_lst)
    # Deep link
    merged_set_lst = []
    while len(set_lst) != 0:
        c_set = set_lst.pop()
        is_merged = False
        for _set in set_lst:
            if len(c_set.intersection(_set)) != 0:
                _set.update(c_set)
                is_merged = True
        if not is_merged:
            if len(merged_set_lst) == 0:
                merged_set_lst.append(c_set)
            else:
                for _set in merged_set_lst:
                    if len(c_set.intersection(_set)) != 0:
                        _set.update(c_set)
                        is_merged = True
                if not is_merged:
                    merged_set_lst.append(c_set)
    if score_vec is None:
        return merged_set_lst
    else:
        discard_set = set()
        _min = min(score_vec)
        assert len(score_vec) == score_mtx.shape[0]
        for _set in merged_set_lst:
            pos = None
            _max = _min
            for item in _set:
                if score_vec[item] >= _max:
                    pos = item
                    _max = score_vec[item]
            _set.remove(pos)
            discard_set.update(_set)
        return list(discard_set)


def pick_file(current_dir, pattern='.pdf', new=True, strict=False):
    if strict:
        files = [item for item in os.listdir(current_dir) if pattern in item]
    else:
        files = [item for item in os.listdir(current_dir) if pattern.lower() in item.lower()]
    file_cts = [os.path.getmtime(os.path.join(current_dir, item)) for item in files]
    if len(file_cts) >= 1:
        if new:
            return files[file_cts.index(max(file_cts))]
        else:
            return files[file_cts.index(min(file_cts))]
    else:
        return None


def rename_with_suffix(file_path, suffix=None):
    assert os.path.exists(file_path)
    if suffix is None:
        suffix = '_' + dt.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y%m%d_%H%M%S')
    base_name = os.path.basename(file_path).split('.')
    if len(base_name) == 1:
        new_name = base_name[0] + suffix
    else:
        new_name = '.'.join(base_name[:-1]) + suffix + '.' + base_name[-1]
    new_file_path = os.path.join(os.path.dirname(file_path), new_name)
    assert not os.path.exists(new_file_path)
    os.rename(file_path, new_file_path)


def fill_rate(pd_raw, return_missing=True, return_list=False):
    # return fill rate of input, possibly return missing indexes
    # fill rate: average cross sectional fill rate or fill rate per day in Series
    # missing dates: time series missing dates
    if type(pd_raw) not in [pd.DataFrame, pd.Series]:
        raise AssertionError
    if isinstance(pd_raw, pd.Series):
        assert isinstance(pd_raw.index, pd.core.index.MultiIndex)
        pd_raw = pd_raw.unstack()
    # pd_raw = pd_raw.dropna(how='all')
    if not return_list:
        _fill_rate = pd_raw.stack().size / pd_raw.size
    else:
        _fill_rate = np.isfinite(pd_raw).sum(axis=1) / pd_raw.shape[1]
    if return_missing:
        begin_date = pd_raw.index[0]
        end_date = pd_raw.index[-1]
        date_range = tdt.get_trading_date_range(begin_date, end_date)
        _missing_dates = [date for date in date_range if date not in pd_raw.index]
        return _fill_rate, _missing_dates
    else:
        return _fill_rate


def deviation_detection(ps, threshold_percentage=0.2):
    # return indexes in pd.Series or indexes in array of points which deviate
    # given percentage away from other points
    if isinstance(ps, np.ndarray):
        ps = pd.Series(ps)
    assert isinstance(ps, pd.Series)
    ps_delta = (ps - ps.shift(1)) / ps * 100
    if ps_delta.sum() < 0:
        ps_delta = - pd_delta  # assert ascending afterwards
    return ps_delta.loc[ps_delta<=-threshold_percentage].index.tolist()


def layer_chopper(ps_raw, layers, rank=True):
    # return pd.Series with categorical tags representing bins to which raw data has been assigned
    # use rank to ensure that each bin contains equal numbers of samples at best situation
    if isinstance(layers, int):
        _labels = range(layers)
    else:
        _labels = range(len(layers) - 1)
    if rank:
        return pd.cut(ps_raw.rank(), layers, retbins=False, labels=_labels)
    else:
        return pd.cut(ps_raw, layers, retbins=False, labels=_labels)


def spread_agg(pd_sorter, pd_data, layers):
    # sorted & data are matrix style pd.DataFrame or pd.Series which can be unstacked
    # sorter is used to generate cross sectional bins
    # data is aggregated according to sorter generated bins
    # default input is assumed to be dates as index(ascending) and stocks as columns
    # returned pd.DataFrame is designed to be dates as index and Quantile information as columns
    if type(pd_sorter) not in [pd.DataFrame, pd.Series]:
        raise AssertionError
    if type(pd_data) not in [pd.DataFrame, pd.Series]:
        raise AssertionError
    if isinstance(pd_sorter, pd.Series):
        pd_sorter = pd_sorter.unstack().dropna(how='all')
    else:
        pd_sorter = pd_sorter.dropna(how='all')
    # perform rank outside to speedup
    pd_bins = pd_sorter.rank(axis=1).apply(layer_chopper, axis=1, layers=layers, rank=False)
    # align / match / retrieve / iterate
    _sorter = pd_bins.stack()
    _sorter.name = 'bins'
    _data = pd_data.stack() if isinstance(pd_data, pd.DataFrame) else pd_data
    _data.name = 'data'
    # for speed reason, only data with information are processed
    _magic = pd.DataFrame(_sorter).merge(pd.DataFrame(_data), how='left', left_index=True, right_index=True).dropna()
    res = []
    for date, grouped in _magic.groupby(level=0):
        sliced_res = grouped.groupby('bins').mean()['data']
        sliced_res.name = date
        res.append(sliced_res)
    pd_res = pd.concat(res, axis=1).T
    pd_res.columns = ['Q'+str(int(col)) for col in pd_res.columns]
    return pd_res


def param_retriever(formula, key, parse=True):
    formula = formula.replace(')', ',').replace(';', ',').split(',')
    for item in formula:
        if '=' in item and key in item:
            _pair = item.split('=')
            if key == _pair[0].strip():
                _res = _pair[1].strip()
                if parse:
                    try:
                        _res = str2num(_res)
                    except ValueError:
                        try:
                            _res = eval(_res)  # bool type
                        except NameError:
                            pass  # string returned
                return _res
    return None


def dict_merge(root, leaf, operator='guess', inplace=True):
    assert isinstance(root, dict)
    assert isinstance(leaf, dict)
    if not inplace:
        root = root.copy()
    for key in leaf:
        if key in root:
            if operator == 'guess':
                if np.any([isinstance(leaf[key], item) for item in [list, tuple]]):
                    root[key].extend(leaf[key])
                else:
                    root[key] += leaf[key]
            elif operator == 'sum':
                root[key] += leaf[key]
            elif operator == 'extend':
                root[key].extend(leaf[key])
            else:
                raise NotImplementedError
        else:
            root[key] = leaf[key]
    if not inplace:
        return root


def add_dict_counts(target_dict, key_list, inplace=True):
    # for keys in key list, ++ target dict value with same key
    assert isinstance(target_dict, dict)
    if not inplace:
        target_dict = target_dict.copy()
    if key_list is None:
        return
    if not isinstance(key_list, list):
        key_list = [key_list]
    for key in key_list:
        if key in target_dict:
            target_dict[key] += 1
        else:
            target_dict[key] = 1
    if not inplace:
        return target_dict


def align_data(data_dict, inner=True):
    # maybe should use dt, Ticker instead
    date_sets, stock_sets = list(), list()
    for factor in data_dict:
        if np.any([isinstance(data_dict[factor], _type) for _type in [pd.DataFrame, pd.Series]]):
            if isinstance(data_dict[factor].index, pd.core.index.MultiIndex):
                if 'dt' == data_dict[factor].index.names[0]:
                    date_sets.append(set(data_dict[factor].index.get_level_values(level=0).unique()))
            else:
                if isinstance(data_dict[factor], pd.DataFrame):
                    assert isinstance(data_dict[factor].index, pd.DatetimeIndex)
                    date_sets.append(set(data_dict[factor].index))
                    stock_sets.append(set(data_dict[factor].columns))
                else:  # Series
                    assert isinstance(data_dict[factor].index, pd.DatetimeIndex)
                    date_sets.append(set(data_dict[factor].index))
        elif isinstance(data_dict[factor], dict):
            for nested_factor in data_dict[factor]:
                if isinstance(data_dict[factor][nested_factor], pd.DataFrame):
                    assert isinstance(data_dict[factor][nested_factor].index, pd.DatetimeIndex)
                    date_sets.append(set(data_dict[factor][nested_factor].index))
                    stock_sets.append(set(data_dict[factor][nested_factor].columns))
        else:
            continue
    date_list = sorted(set.intersection(*date_sets) if inner else set.union(*date_sets))
    stock_list = sorted(set.intersection(*stock_sets) if inner else set.union(*stock_sets))
    data_dict_aligned = {}
    for factor in data_dict:
        if np.any([isinstance(data_dict[factor], _type) for _type in [pd.DataFrame, pd.Series]]):
            if isinstance(data_dict[factor].index, pd.core.index.MultiIndex):
                if 'dt' == data_dict[factor].index.names[0]:  # MultiIndex actually will not fillna
                    data_dict_aligned[factor] = data_dict[factor].reindex(index=date_list, level=0)
            else:
                if isinstance(data_dict[factor], pd.DataFrame):
                    data_dict_aligned[factor] = data_dict[factor].reindex(index=date_list, columns=stock_list)
                else:
                    data_dict_aligned[factor] = data_dict[factor].reindex(index=date_list)
        elif isinstance(data_dict[factor], dict):
            data_dict_aligned[factor] = {}
            for nested_factor in data_dict[factor]:
                if isinstance(data_dict[factor][nested_factor], pd.DataFrame):
                    data_dict_aligned[factor][nested_factor] = data_dict[factor][nested_factor].reindex(
                                                               index=date_list, columns=stock_list)
    return data_dict_aligned


def regression_ols(y, x):
    # calculate ols problem given y as DataFrame and x as dictionary with DataFrames of regressors
    assert(isinstance(x, dict))
    date_num, stock_num = y.shape
    x_list = list(x.keys())
    contains_industry = True if 'Industry' in x_list else False
    x_num = len(x_list) - 1 if contains_industry else len(x_list)
    x_mat = np.ones([x_num, date_num, stock_num])
    y_mat = np.array(y)
    r2_mat = np.empty(date_num)
    r2_mat[:] = np.nan
    beta_mat = np.empty([date_num, x_num+1])
    beta_mat[:] = np.nan
    tstats_mat = beta_mat.copy()
    res_mat = np.full_like(y, np.nan, dtype=np.double)
    if contains_industry:
        ind_mat = np.array(x['Industry'])
        x_list.remove('Industry')
    i = 0
    for x_name in x_list:
        x_mat[i, :, :] = np.array(x[x_name])
        i = i + 1
    for date_idx in range(date_num):
        if contains_industry:
            ind_dum = pd.get_dummies(ind_mat[date_idx, :]).values
            _x = np.column_stack([x_mat[:, date_idx, :].T, ind_dum])
        else:
            _x = x_mat[:, date_idx, :].T
        try:
            res_mat[date_idx, :], r2_mat[date_idx], beta_mat[date_idx, :], tstats_mat[date_idx, :] = stats_model_ols(y_mat[date_idx, :], _x)
        except ValueError:
            pass
    res = pd.DataFrame(res_mat, columns=y.columns, index=y.index)
    r2 = pd.Series(r2_mat, index=y.index)
    beta = pd.DataFrame(beta_mat, columns=['intercept']+x_list, index=y.index)
    tstats = pd.DataFrame(tstats_mat, columns=['intercept']+x_list, index=y.index)
    return res, r2, beta, tstats


def stats_model_ols(y, x, min_percentage=10):
    res = np.full_like(y, np.nan, dtype=np.double)
    mask = np.isfinite(y + x.sum(axis=1))
    if np.count_nonzero(mask) / len(mask) * 100 < min_percentage:
        raise ValueError
    ols = resider(x[mask], y[mask], method='sm.OLS', add_const=True, mean_only=False, r_square=False, return_sm=True)
    res[mask] = ols.resid
    return res, ols.rsquared, ols.params, ols.tvalues


def sniper(best_before):
    try:
        import multifactor.utility.ntplib as ntplib
        _ntp = ntplib.NTPClient()
        # UTC time
        now = dt.datetime.utcfromtimestamp(_ntp.request('cn.pool.ntp.org').tx_time)
    except (ImportError, ntplib.NTPException):
        now = dt.datetime.now()
    if now > best_before:
        return True
    else:
        return False


def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    for block in bytesiter:
        hasher.update(block)
    return (hasher.hexdigest() if ashexstr else hasher.digest())


def file_as_blockiter(file_name, blocksize=65536):
    with open(file_name, 'rb') as fin:
        block = fin.read(blocksize)
        while len(block) > 0:
            yield block
            block = fin.read(blocksize)


def file_hasher(file_name, hasher=hashlib.sha256, ashexstr=True):
    return hash_bytestr_iter(file_as_blockiter(file_name), hasher(), ashexstr=ashexstr)


def weight_decay(half_life, total_len):
    # return exponential weights with last element the biggest
    res = np.array([0.5 ** ((total_len - i) / half_life) for i in range(total_len)])
    return res / np.sum(res)


def zip_apply(x, y, func):
    return np.array([func(*i) for i in zip(x.ravel(), y.ravel())])


def issusing_date_deadline_helper(x):
    x = IO.str_date_parser(x)
    y, m, d = x.year, x.month, x.day
    if (m, d) == (3, 31):
        return pd.Timestamp(x.year, 4, 30)
    elif (m, d) == (6, 30):
        return pd.Timestamp(x.year, 8, 31)
    elif (m, d) == (9, 30):
        return pd.Timestamp(x.year, 10, 31)
    elif (m, d) == (12, 31):
        return pd.Timestamp(x.year + 1, 4, 30)
    else:
        raise AssertionError


def issuing_date_checker(issuing_date_ps):
    # remove issuing dates not in the ascending order
    # eg: annual report later than 1st quarter report, remove annual report issuing date
    # caution: DataFrame & timedelta comparison is buggy
    if not isinstance(issuing_date_ps.iloc[0], pd.Timestamp):
        issuing_date_ps = pd.to_datetime(issuing_date_ps)
    data = issuing_date_ps.unstack()
    report_dead_line = pd.DataFrame(data.index, index=data.index)
    report_dead_line['dead_line'] = report_dead_line['dt'].apply(issusing_date_deadline_helper)
    # check for non-ascending issuing date
    _days = (data - data.shift(-1)).apply(lambda x: x.dt.days)
    _mask_1 =  (_days > 0) & (_days < 1000)
    # check for issuing date later than dead line
    _mask_2 = (data.subtract(report_dead_line['dead_line'], axis=0)).apply(lambda x: x.dt.days) >= 30
    # check for wrong issuing date
    _mask_3 = (data.subtract(report_dead_line['dt'], axis=0)).apply(lambda x: x.dt.days) <= -1
    _mask = _mask_1 | _mask_2 | _mask_3
    data[_mask] = np.nan
    return data.stack()


def delisting_days_shifted(shift_days=None, h5_path=ionc.listing_delisting_path):
    with pd.HDFStore(h5_path, 'r') as hdf_store:
        delist_date = hdf_store.SecDate.delist_date.reset_index()
        if shift_days is not None:
            # get current calendar max days for shift purpose and speed
            calendar_max = tdt.get_calendar_max_date()
            delist_date = delist_date.loc[delist_date['delist_date'] < calendar_max].reset_index(drop=True)
            delist_date['delist_date'] = delist_date['delist_date'].apply(lambda x: tdt.get_trading_day_offset(x, shift_days)[0])
        delist_date = delist_date.set_index(['Ticker'])['delist_date'].sort_index()
    return delist_date


def create_listing_delisting_filter(start_date, end_date, merged_mask=True,
                                    h5_path=ionc.listing_delisting_path):
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    full_day_range = pd.date_range(start=start_date, end=end_date, freq='1D')
    trading_dates = tdt.get_trading_date_range(start_date, end_date)
    with pd.HDFStore(h5_path, 'r') as hdf_store:
        delist_date = hdf_store.SecDate.delist_date
        list_date = hdf_store.SecDate.ipo_date
    # process delisting date filter
    delist_date = delist_date.reset_index()
    delist_date['Filter'] = True
    delist_date_pd = delist_date.set_index(['delist_date', 'Ticker'])['Filter'].unstack().reindex(index=full_day_range)
    delist_date_pd = delist_date_pd.fillna(method='ffill')
    delist_date_pd = delist_date_pd.reindex(index=trading_dates)
    delist_date_pd = delist_date_pd.fillna(False).astype('bool')
    # process listing date filter
    list_date = list_date.reset_index()
    list_date['Filter'] = True
    list_date_pd = list_date.set_index(['ipo_date', 'Ticker'])['Filter'].unstack().reindex(index=full_day_range)
    list_date_pd = list_date_pd.fillna(method='bfill')
    list_date_pd = list_date_pd.reindex(index=trading_dates)
    list_date_pd = list_date_pd.fillna(False).astype('bool')
    if merged_mask:
        return delist_date_pd | list_date_pd
    else:
        return delist_date_pd, list_date_pd


def backfill_date_helper(start_date, end_date, delay=240):
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    _start_date = tdt.get_trading_day_offset(start_date, -delay)[0]
    return _start_date, end_date


def backfill_data_helper(start_date, end_date, dtype):
    start_date, end_date = backfill_date_helper(start_date, end_date)
    if dtype == 'issuing_date':
        issuing_date_ps = IO.read_data([start_date, end_date], ftype=FType.FDD, dsource=DSource.WIND,
                                        dfreq=DFreq.QUARTERLY, columns=['stm_issuingdate'])['stm_issuingdate']
        return issuing_date_checker(issuing_date_ps)
    elif dtype == 'trading_date':
        return tdt.get_trading_date_range(start_date, end_date)
    elif dtype == 'listing_delisting_filter':
        return create_listing_delisting_filter(start_date, end_date)
    else:
        raise NotImplementedError


def backfill(start_date, end_date, factor_qtr_pd, issuing_date_ps=None, trading_date_list=None,
             issue_date_reformed=False, fast_mode=False, listing_delisting_filter=None, return_unstacked=False):
    # factor_qtr_pd should contain more data than start date and end date
    # to ensure the beginning of backfilled is not empty
    assert len(factor_qtr_pd.columns) == 1
    start_date = IO.str_date_parser(start_date)
    end_date = IO.str_date_parser(end_date)
    _start_date, _end_date = backfill_date_helper(start_date, end_date)
    if issuing_date_ps is None:
        issuing_date_ps = backfill_data_helper(start_date, end_date, dtype='issuing_date')
    else:
        if not issue_date_reformed:
            issuing_date_ps = issuing_date_checker(issuing_date_ps)
    # shift stm issuing date to trading date
    issuing_date_ps = issuing_date_ps.apply(tdt.round_to_trading_date)
    data = factor_qtr_pd.copy()
    data['issuing_date'] = issuing_date_ps
    data = data.reset_index().sort_values(by='dt').dropna()
    data = data.drop_duplicates(subset=['issuing_date', 'Ticker'], keep='last')
    data = data.set_index(['issuing_date', 'Ticker'])
    data = data[factor_qtr_pd.columns[0]].unstack()
    full_day_range = pd.date_range(start=_start_date, end=_end_date, freq='1D')
    data = data.reindex(index=full_day_range).fillna(method='ffill', limit=210)
    if not fast_mode:
        if listing_delisting_filter is None:
            listing_delisting_filter = backfill_data_helper(start_date, end_date, dtype='listing_delisting_filter')
        listing_delisting_filter = listing_delisting_filter.reindex(columns=data.columns).fillna(False).astype('bool')
        data[listing_delisting_filter] = np.nan
    else:
        if listing_delisting_filter is not None:
            warnings.warn('Fast Mode with Non-Empty Listing-Delisting Filter Input', RuntimeWarning)
    if trading_date_list is None:
        data = data.reindex(index=backfill_data_helper(start_date, end_date, dtype='trading_date'))
    else:
        data = data.reindex(index=trading_date_list)
    data = data.loc[start_date:end_date]
    if return_unstacked:
        res = data
        res.index.names = ['dt']
    else:
        res = pd.DataFrame(data.stack(), columns=factor_qtr_pd.columns)
        res.index.names = ['dt', 'Ticker']
    return res


def backfill_cached(start_date, end_date, fast_mode):
    # prepare stage for backfill by decorator & closure
    # usage: backfill_reloaded = backfill_cached(start_date=xxx, end_date=xxx, fast_mode=xxx)
    # filled = backfill_reloaded(to_fill_pd)
    issuing_date_ps = backfill_data_helper(start_date, end_date, dtype='issuing_date')
    trading_date_list = backfill_data_helper(start_date, end_date, dtype='trading_date')
    if not fast_mode:
        listing_delisting_filter = backfill_data_helper(start_date, end_date, dtype='listing_delisting_filter')
    def decorated(factor_qtr_pd, **kwargs):
        if fast_mode:
            return backfill(start_date, end_date, factor_qtr_pd,
                            issuing_date_ps=issuing_date_ps,
                            trading_date_list=trading_date_list,
                            issue_date_reformed=True,
                            fast_mode=True, **kwargs)
        else:
            return backfill(start_date, end_date, factor_qtr_pd,
                            issuing_date_ps=issuing_date_ps,
                            trading_date_list=trading_date_list,
                            issue_date_reformed=True,
                            fast_mode=False,
                            listing_delisting_filter=listing_delisting_filter,
                            **kwargs)
    return decorated


class BackFill:
    def __init__(self, start_date, end_date, fast_mode,
                 in_boilerplate=None, out_boilerplate=None):
        self.start_date = IO.str_date_parser(start_date)
        self.end_date = IO.str_date_parser(end_date)
        self.issuing_date_ps = backfill_data_helper(self.start_date, self.end_date, dtype='issuing_date')
        self.trading_date_list = backfill_data_helper(self.start_date, self.end_date, dtype='trading_date')
        self.fast_mode = fast_mode
        if not self.fast_mode:
            self.listing_delisting_filter = backfill_data_helper(self.start_date, self.end_date, dtype='listing_delisting_filter')
        else:
            self.listing_delisting_filter = None
        self.in_boilerplate = in_boilerplate
        self.out_boilerplate = out_boilerplate

    def __call__(self, factor_qtr_pd):
        if self.in_boilerplate is not None:
            assert isinstance(factor_qtr_pd, np.ndarray)
            factor_qtr_pd = pd.DataFrame(pd.DataFrame(factor_qtr_pd, index=self.in_boilerplate.index,
                                         columns=self.in_boilerplate.columns).stack(), columns=['factor'])
            return_unstacked = True
        else:
            return_unstacked = False
        res = backfill(self.start_date, self.end_date, factor_qtr_pd,
                       issuing_date_ps=self.issuing_date_ps,
                       trading_date_list=self.trading_date_list,
                       issue_date_reformed=True,
                       fast_mode=self.fast_mode,
                       listing_delisting_filter=self.listing_delisting_filter,
                       return_unstacked=return_unstacked)
        if self.out_boilerplate is not None:
            res = res.reindex(index=self.out_boilerplate.index,
                              columns=self.out_boilerplate.columns)
            return res.values
        else:
            return res


def collapse(raw):
    # transform np.array / pd.DataFrame of repeated values into unique values
    if isinstance(raw, np.ndarray):
        pd_raw = pd.DataFrame(raw)
    elif isinstance(raw, pd.DataFrame):
        pd_raw = raw
    else:
        raise AssertionError
    size_lst = []
    unique_index_lst = []
    unique_value_lst = []
    for col in pd_raw.columns:
        _ = pd_raw[col].drop_duplicates().dropna()
        size_lst.append(_.shape[0])
        unique_index_lst.append(_.index)
        unique_value_lst.append(_.values)
    res = np.empty((max(size_lst), pd_raw.shape[1]), dtype=np.double)
    res[:] = np.nan
    for idx, col in enumerate(unique_value_lst):
        res[-len(col):, idx] = col
    return res, unique_index_lst


class HidePrints:
    def __init__(self, hide_err=False):
        self.hide_err = hide_err
        self._original_stdout = None
        self._original_stderr = None

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = None
        if self.hide_err:
            self._original_stderr = sys.stderr
            sys.stderr = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        if self.hide_err:
            sys.stderr = self._original_stderr


class VoidLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


def add_file_logger(name, level=None, file_name=None, mode='a',
                    format_str ='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    lazy_mode=False, void_flag=False):
    if void_flag:  # multiprocessing dummy
        return VoidLogger()
    logger = logging.getLogger(name)
    if lazy_mode:
        return logger
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.DEBUG)
    if file_name is not None:
        if not logger.hasHandlers():
            _dirname = os.path.dirname(file_name)
            if len(_dirname) != 0 and not os.path.exists(_dirname):
                os.makedirs(_dirname)
            file_handler = logging.FileHandler(file_name, mode=mode)
            file_handler.setFormatter(logging.Formatter(format_str))
            logger.addHandler(file_handler)
    else:
        if not logger.hasHandlers():
            # default to screen
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(logging.Formatter(format_str))
            logger.addHandler(stream_handler)
    return logger


def index_slicer(pd_raw, mark_lst, level=0):
    # index in pd_raw is expected to be ascending
    mark_lst = sorted(mark_lst)
    idx_lst = pd_raw.index.get_level_values(level=level).tolist()
    idx_dic = dict()
    for idx, mark in enumerate(mark_lst):
        try:
            if idx == 0:
                idx_dic[mark] = idx_lst.index(mark)
            else:
                _start = idx_dic[mark_lst[idx-1]]
                _start = 0 if _start is None else _start
                idx_dic[mark] = idx_lst.index(mark, _start)
        except ValueError:
            idx_dic[mark] = None
    return idx_dic


def h5_helper(h5_path, operation):
    if operation in ['append', 'create']:
        if operation == 'create':
            append_mode = None
            from_scratch = True
            if os.path.exists(h5_path):
                if query_yes_no('H5 file already exists, delete stale?', 'yes', 30):
                    os.remove(h5_path)
                else:
                    raise AssertionError
            else:
                if not os.path.exists(os.path.dirname(h5_path)):
                    os.makedirs(os.path.dirname(h5_path))
        else:
            append_mode = True
            from_scratch = False
    else:
        raise AssertionError
    return append_mode, from_scratch


class NoDaemonProcess(multiprocessing.Process):
    # make 'daemon' attribute always return False
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

# sub-class multiprocessing.pool.Pool instead of multiprocessing.Pool
# because the latter is only a wrapper function, not a proper class.
class MyPool(multiprocessing.pool.Pool):
    Process = NoDaemonProcess


def timedelta_helper(item):
    hours = int(item / 10000000)
    item -= hours * 10000000
    minutes = int(item / 100000)
    item -= minutes * 100000
    seconds = int(item / 1000)
    item -= seconds * 1000
    milliseconds = item
    return pd.Timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)


def dict_fillna(dic, value=0):
    res = dict()
    for k, v in dic.items():
        if np.isnan(v):
            res[k] = value
        else:
            res[k] = v
    return res


def recursive_map (seq, func):
    for item in seq:
        if isinstance(item, Sequence):
            yield type(item)(recursive_map(item, func))
        else:
            yield func(item)


def ps_helper(ps_raw):
    if isinstance(ps_raw, pd.DataFrame):
        assert len(ps_raw.columns) == 1
        res = ps_raw.iloc[:, 0]
        res.name = ps_raw.columns[0]
    elif isinstance(ps_raw, pd.Series):
        res = ps_raw
    else:
        raise NotImplementedError
    return res


def deepcopied_vars(obj):
    cfg = dict()
    _cfg = vars(obj) if not isinstance(obj, dict) else obj
    for key in _cfg:
        try:
            cfg[key] = copy.deepcopy(_cfg[key])
        except Exception as _exp:
            print('%s encountered during dumping %s' % (_exp, key))
            continue
    return cfg


def permute_symmetric(x, i, j):
    x = x.copy()
    x[:, [i, j]] = x[:, [j, i]]
    x[[i, j], :] = x[[j, i], :]
    return x


def nan_weighted_stats(x, w, method=None):
    # weighted statistics cannot be simply computed by numpy
    x = np.ma.masked_invalid(x)
    _x = x.data[~x.mask]
    _w = w[~x.mask]
    assert not np.isnan(_w).any()
    _w = _w * (len(_w) / np.sum(_w))
    inst = DescrStatsW(_x, weights=_w)
    if method is None:
        return inst
    else:
        if len(_x) == 0:
            return np.nan
        else:
            return getattr(inst, method)


def weighted_stats_along_axis(raw, weight, method, axis=0):
    assert raw.shape[axis] == len(weight)
    if isinstance(raw, pd.DataFrame):
        return raw.apply(nan_weighted_stats, axis=axis, w=weight, method=method)
    elif isinstance(raw, np.ndarray):
        return np.apply_along_axis(nan_weighted_stats, axis, raw, w=weight, method=method)


def rolling_ewm(pd_raw, window, half_life, method='mean', min_weight=0.5):
    # Fixed window rolling ewma along axis 0 for DataFrame
    if isinstance(pd_raw, pd.DataFrame):
        x_mat = pd_raw.values
    elif isinstance(pd_raw, np.ndarray):
        x_mat = pd_raw
        assert len(x_mat.shape) == 2
    else:
        raise NotImplementedError
    weight = weight_decay(half_life, window)
    row_num, col_num = x_mat.shape
    y_mat = np.full_like(x_mat, fill_value=np.nan, dtype=np.double)
    dummy_weight = (np.ones([window, col_num]).T * weight).T
    for i in range(window, row_num+1):
        x_sliced = x_mat[i-window:i, :]
        x_mask = np.isfinite(x_sliced)
        col_weight = (x_mask * dummy_weight).sum(axis=0)
        col_mask = col_weight >= min_weight
        if not np.all(~col_mask):
            y_mat[i-1, col_mask] = weighted_stats_along_axis(x_sliced[:, col_mask],
                                                             weight=weight, method=method, axis=0)
    if isinstance(pd_raw, pd.DataFrame):
        res = pd.DataFrame(y_mat, index=pd_raw.index, columns=pd_raw.columns)
    else:
        res = y_mat
    return res


def rolling_ts_regression(x, y, look_back_days, half_life=None, x_type='macro', method='std'):
    # assume x with dimension (n, l) or (n, m)
    # assume y with dimension (n, m)
    # n is date number, m is stock number, l is macro feature number
    # if l == m, assume x, y are two factors for ts regression
    assert isinstance(x, np.ndarray) and isinstance(y, np.ndarray)
    w = weight_decay(half_life, look_back_days) if half_life is not None else 1
    date_num, stock_num = x.shape[0], y.shape[1]
    res = np.full_like(y, np.nan, dtype=np.double)
    rsquared = np.full_like(y, np.nan, dtype=np.double)
    if x_type == 'macro':
        beta = np.full_like(np.empty((date_num, stock_num, x.shape[1]+1)), np.nan, dtype=np.double)
        tvalues = np.full_like(np.empty((date_num, stock_num, x.shape[1]+1)), np.nan, dtype=np.double)
    else:
        beta = np.full_like(np.empty((date_num, stock_num, 2)), np.nan, dtype=np.double)
        tvalues = np.full_like(np.empty((date_num, stock_num, 2)), np.nan, dtype=np.double)
    if date_num < look_back_days:
        raise AssertionError('stock return date number less than required')
    for i in range(look_back_days, date_num):
        X = x[i-look_back_days:i, :]
        Y = y[i-look_back_days:i, :]
        X_decay = (X.T * w).T
        Y_decay = (Y.T * w).T
        for j in range(stock_num):
            try:
                if x_type == 'macro':
                    _res, _rsquared, _beta, _tvalues = stats_model_ols(Y_decay[:, j], X_decay)
                else:
                    _res, _rsquared, _beta, _tvalues = stats_model_ols(Y_decay[:, j], X_decay[:, j])
                # residuals should be transformed back without weight interferences
                _res = _res / w
                res[i, j] = nan_weighted_stats(_res, w, method)
                rsquared[i, j] = _rsquared
                beta[i, j, :] = _beta
                tvalues[i, j, :] = _tvalues
            except ValueError:
                continue
    return res, rsquared, beta, tvalues


def pd_matrix_reshaper(pd_raw):
    if isinstance(pd_raw.index, pd.core.index.MultiIndex):
        if isinstance(pd_raw, pd.Series):
            _pd_raw = pd_raw.unstack()
        elif isinstance(pd_raw, pd.DataFrame):
            assert len(pd_raw.columns) == 1
            _pd_raw = pd_raw[pd_raw.columns[0]].unstack()
        else:
            raise AssertionError
    else:
        assert isinstance(pd_raw, pd.DataFrame)
        assert len(pd_raw.columns) > 1
        _pd_raw = pd_raw.copy()
    return _pd_raw


def pd_to_csv(pd_raw, root_path):
    pd_raw = pd_matrix_reshaper(pd_raw)
    if not os.path.exists(root_path):
        os.makedirs(root_path)
    for rec in pd_raw.itertuples():
        _rec = pd.Series(rec[1:], index=pd_raw.columns).dropna()
        _name = os.path.join(root_path, rec[0].strftime('%Y%m%d') + '.csv')
        _rec.to_csv(_name, header=False)


def h5_to_csv(h5_file, root_path, override=True, subfolder=True):
    pd_raw = IO.read_data(alt=h5_file)
    assert len(pd_raw.columns) == 1
    if subfolder:
        _name = pd_raw.columns[0]
        _root_path = os.path.join(root_path, _name)
    else:
        _root_path = root_path
    if not os.path.exists(_root_path):
        os.makedirs(_root_path)
    if override:
        pd_to_csv(pd_raw, _root_path)
    else:
        csv_lists = sorted([item.split('.')[0] for item in os.listdir(_root_path) if '.csv' in item])
        if len(csv_lists) != 0:
            end_date = csv_lists[-1]
            pd_to_csv(pd_raw.loc[tdt.get_trading_day_offset(end_date, 1)[0]:], _root_path)
        else:
            pd_to_csv(pd_raw, _root_path)


def csv_to_h5(root_path, h5_file_path, dataset, factor_name,
              start_date=None, end_date=None, from_scratch=True, header_exist=False):
    start_date = IO.str_date_parser(start_date) if start_date is not None else pd.Timestamp.min
    end_date = IO.str_date_parser(end_date) if end_date is not None else pd.Timestamp.max
    file_list = list()
    for item in os.listdir(root_path):
        _date = IO.str_date_parser(os.path.basename(item).split('.')[0])
        if start_date <= _date <= end_date:
            file_list.append(os.path.join(root_path, item))
    IO.csv_dumper(file_list, hdf5=h5_file_path, dataset=dataset, from_scratch=from_scratch,
                  header_exist=header_exist, factor_name=factor_name)


def max_drawdown_ts(cum_return_ps, interest_type='SIMPLE', return_drawdown_period=False):
    assert isinstance(cum_return_ps, pd.Series)
    cum_return_ps = cum_return_ps.fillna(0)
    cum_max = np.maximum.accumulate(cum_return_ps)
    if interest_type == 'SIMPLE':
        mdd_ts = cum_return_ps - cum_max
    else:
        mdd_ts = (cum_return_ps - cum_max) / cum_max
    mdd_idx = mdd_ts.idxmin()
    mdd_max_level = cum_max.loc[mdd_idx]
    _ = cum_return_ps.loc[:mdd_idx]
    try:
        mdd_begin_idx = _[_ == mdd_max_level].index[-1]
    except IndexError:
        mdd_begin_idx = pd.NaT
    _ = cum_return_ps.loc[mdd_idx:]
    try:
        mdd_end_idx = _[_ >= mdd_max_level].index[0]
    except IndexError:
        mdd_end_idx = pd.NaT
    if return_drawdown_period:
        return mdd_ts, (mdd_begin_idx, mdd_end_idx)
    else:
        return mdd_ts


def calc_cum_return_ts(return_ps, interest_type='SIMPLE'):
    if interest_type == 'SIMPLE':
        res = return_ps.cumsum() + 1
    else:
        res = (return_ps + 1).cumprod()
    return res


def calc_annualized_return(return_ps, interest_type='SIMPLE'):
    year_date_num = calc_year_date_num(return_ps)
    if interest_type == 'SIMPLE':
        res = return_ps.mean() * year_date_num
    else:
        _ = calc_cum_return_ts(return_ps, interest_type=interest_type)
        if isinstance(_, np.ndarray):
            res = _[-1] ** (year_date_num / len(return_ps)) - 1
        else:
            res = _.iloc[-1] ** (year_date_num / len(return_ps)) - 1
    return res


def calc_year_date_num(ps_raw):
    predefined_num = 252
    if isinstance(ps_raw, np.ndarray):
        return predefined_num
    year_list = list(ps_raw.index.year.unique())
    date_num_list = list()
    try:
        for year in year_list:
            year_date_num = len(tdt.get_trading_date_range(dt.datetime(year=int(year), month=1, day=1),
                                                           dt.datetime(year=int(year), month=12, day=31)))
            date_num_list.append(year_date_num)
    except OSError:
        print('Cannot Retrieve Calendar Data')
        return predefined_num
    return np.mean(date_num_list)


def query_yes_no(question, default="yes", timeout=None):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = InputWithTimeout(default, timeout).input.lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


class InputWithTimeout:
    _input = None

    def __init__(self, default=None, timeout=20):
        self.__class__._input = default
        get_input_thread = threading.Thread(target=self.get_input, daemon=True)
        get_input_thread.start()
        get_input_thread.join(timeout=timeout)

    @property
    def input(self):
        return self.__class__._input

    @classmethod
    def get_input(cls):
        cls._input = input()


def shrink(x):
    assert isinstance(x, list)
    if len(x) >= 2:
        x[1] = re.sub('selected', x[0], x[1])
        x[1] = re.sub('upstream_(\d+?)', lambda m: x[0] + '[' + m.group(1) + ']', x[1])
        x = shrink(x[1:])
    else:
        x = x[0]
    return x


def formulate(x):
    # transform -> style to normal math form
    x = re.sub('%(.+?)%', lambda m: formulate(m.group(1)), x)
    return shrink([item.replace(':', '(') + ')' for item in x.replace('$', '').replace(' ', '').split(';')[:-1]])


def decorated_formulate(x):
    # transform -> style to normal math form in cleaner form
    x = formulate(x)
    x = x.replace('timeperiod', 't')
    x = re.sub('(,)?return_distance=(True|False)', '', x)
    x = re.sub('(,)?quick_return=(True|False)', '', x)
    x = re.sub('(,)?smart_cast=(True|False)', '', x)
    return x


def sublimate(x, include_operator=False):
    # retrieve input ingredients for the given formula
    x = x.replace(':', ',').replace(';', ',').replace(' ', '').split(',')
    if not include_operator:
        x = [i for i in x if not any([j in i for j in ['selected', 'upstream', '$', '=']])]
    else:
        x = [i.replace('%', '') for i in x if not any([j in i for j in ['selected', 'upstream', '=']])]
    return x


def element_coverage(factors, include_operator=False):
    fct_elements = [sublimate(i, include_operator=include_operator) for i in factors]
    aset = set().union(*fct_elements)
    adict = dict(zip(aset, [0] * len(aset)))
    for ele in aset:
        adict[ele] = sum([ele in i for i in fct_elements]) / len(fct_elements)
    return adict


def calculate_limit_prices(pre_close, places=2, limit=0.1):
    return round_half_up(pre_close * (1 + limit), places), round_half_up(pre_close *(1 - limit), places)


def round_half_up(x, places=0):
    x = Decimal(x).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
    if places == 0:
        x = int(x)
    else:
        x = float(x)
    return x


def is_limit_price(pre_close, price, ticker):
    tag = 0
    if 'ST' in ticker:
        up, down = calculate_limit_prices(pre_close, limit=0.05)
    else:
        up, down = calculate_limit_prices(pre_close)
    if price == up:
        tag = 1
    elif price == down:
        tag = -1
    else:
        tag = 0
    return tag


def flatten_dict(x):
    _x = copy.deepcopy(x)
    for k, v in x.items():
        if isinstance(v, dict):
            for nk, nv in v.items():
                _x[':'.join([k, nk])] = nv
            del _x[k]
    return _x


def deep_flatten_dict(x):
    while np.any([isinstance(item, dict) for item in x.values()]):
        x = flatten_dict(x)
    return x


def nested_dict_content_type_cast(x, attr=None, func=None):
    assert isinstance(x, dict)
    assert (attr is not None) or (func is not None)
    y = dict()
    for k in x:
        if not isinstance(x[k], dict):
            if attr is not None:
                y[k] = getattr(x[k], attr)()
            if func is not None:
                y[k] = func(x[k])
        else:
            y[k] = nested_dict_content_type_cast(x[k], attr=attr, func=func)
    return y


def retrieve_style_factors(trading_days, columns=None, industry_name='CITIC_I', dummify=True,
                           split_industry=False, dsource='DERIVED'):
    assert dsource in ['DERIVED', 'RISK']
    if columns is not None:
        assert isinstance(columns, list)
        if dsource == 'DERIVED':
            _columns = [item.lower() for item in columns if item != 'Industry']
        elif dsource == 'RISK':
            _columns = columns
    else:
        _columns = None
    if dsource == 'DERIVED':
        style_pd = IO.read_data(trading_days, columns=_columns,
                                dsource=DSource.DERIVED,  dtable=DTable.DERIVED_barra, h5root=ionc.private_h5root)
        style_pd.columns = [''.join([j.capitalize() for j in i.split('_')]) for i in style_pd.columns]
    elif dsource == 'RISK':
        style_pd = IO.read_data(trading_days, columns=_columns,
                                ftype=FType.RISK, dsource=DSource.STYLEFACTOR)
    # Process industry
    if columns is None or 'Industry' in columns:
        if dsource == 'DERIVED':
            ind = IO.read_data(trading_days, ftype=FType.INDUSTRY, dsource=DSource.WIND, columns=industry_name)
            ind.columns = ['Industry']
        else:
            ind = style_pd[['Industry']]
        if dummify:
            ind = pd.get_dummies(ind['Industry'])
            ind.columns = ['ind' + str(int(item)) for item in ind.columns]
            ind = ind.drop('ind0', axis=1, errors='ignore')
        style_pd = style_pd.drop(['Industry'], axis=1, errors='ignore')
        if split_industry:
            return style_pd, ind
        style_pd = style_pd.join(ind)
    return style_pd


def turnover_estimate(pd_raw, holding_period=1, sign=1, quantile=0.9, round_trip=True):
    assert sign in [1, -1]
    pd_raw = sign * pd_raw
    # reshape to matrix style and resample according to holding period
    pd_raw = pd_matrix_reshaper(pd_raw).iloc[::holding_period, :]
    ps_lim = pd_raw.quantile(q=quantile, axis=1)
    pd_selected = pd_raw.subtract(ps_lim, axis=0) >= 0
    turnover = pd_selected.astype('float64').diff().abs().sum(axis=1).divide(pd_selected.sum(axis=1)).replace(
                                                                     [np.inf, -np.inf], np.nan).mean()
    if round_trip:
        return turnover
    else:
        return turnover / 2

def acronym(phrase, min_len=6, seq=2):
    res = ''
    assert isinstance(phrase, str)
    if len(phrase) <= min_len:
        res = phrase
    else:
        seq_counter = seq
        for l in phrase:
            if l.isupper():
                res += l
                seq_counter = 0
            elif seq_counter < seq:
                res += l
                seq_counter += 1
    return res

def acronyms(phrases):
    assert not isinstance(phrases, str)
    return [acronym(item) for item in phrases]


def calc_universe_weight(trading_days, universe='alpha_universe', equal_weight=False):
    univ = IO.read_data(trading_days, columns=ionc.universe_mapper[universe], ftype=FType.UNIV, dsource=DSource.OPTM).fillna(False)
    univ = univ.loc[univ[ionc.universe_mapper[universe]]][ionc.universe_mapper[universe]]
    if equal_weight:
        univ_weight = univ.divide(univ.groupby('dt').sum(), level=0)
    else:
        md = IO.read_data(trading_days, columns=['free_float_shares', 'close'])
        ff_cap = md['free_float_shares'] * md['close']
        ff_cap = ff_cap.reindex(univ.index)
        univ_weight = ff_cap.divide(ff_cap.groupby('dt').sum(), level=0)
    univ_weight.name = universe + '_weight'
    return univ_weight


def batch_replace_in_file(file_name, mapping_dict, new_file_name=None):
    if isinstance(mapping_dict, str):
        with open(mapping_dict, 'r') as f:
            mapping_dict = O0O0O0([item.strip() for item in f.read().split()])
    assert isinstance(mapping_dict, dict)
    with open(file_name) as f:
        s = f.read()
    for k, v in mapping_dict.items():
        s = s.replace(k, v)
    if new_file_name is None:
        if not query_yes_no('override old file? [Y/n]'):
            return
        new_file_name = file_name
    with open(new_file_name, 'w') as f:
        f.write(s)


def O0O0O0(keys, encoding_length=10):
    assert not isinstance(keys, str)
    assert isinstance(keys, Iterable)
    values = set()
    while True:
        values.add('O' + ''.join(np.random.choice(['0', 'O'], size=encoding_length - 1)))
        if len(values) == len(keys):
            break
    return dict(zip(keys, values))


@functools.lru_cache(maxsize=None)
def ticker_match(ticker_num):
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num >= 600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num))) * '0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker


def dt_ticker_reformat(dat, format_str='%Y%m%d'):
    dat = dat.reset_index()
    dat['Ticker'] = dat['Ticker'].apply(ticker_match)
    dat['dt'] = pd.to_datetime(dat['dt'], format=format_str)
    dat = dat.set_index(['dt', 'Ticker'])
    return dat


def multivariate_agg(pd_raw, target_col, filter_cfg, qcut=False, method='mean'):
    # use filter cfg cols to split high dimensional space into
    # cubes and calculate target col stats in the above cubes
    # filter_cfg: {'split_col': bins / nbins}
    assert isinstance(pd_raw, pd.DataFrame)
    pd_raw = pd_raw.reset_index(drop=True)
    for col, rule in filter_cfg.items():
        if qcut:
            pd_raw[col] = pd.qcut(pd_raw[col], q=rule)
        else:
            pd_raw[col] = pd.cut(pd_raw[col], bins=rule)
    return getattr(pd_raw.groupby(list(filter_cfg.keys()))[target_col], method)()


def is_valid_ticker(x):
    return x.startswith(('0', '3', '6'))


def filter_invalid_ticker(x):
    # given iterable x of tickers, return list of valid tickers
    assert isinstance(x, Iterable)
    return [i for i in x if is_valid_ticker(i)]


def get_spring_festival_date(current_date, flag):
    # return previous or next spring festival date regarding input date
    # previous flag returns same date if input date is spring festival
    current_date = IO.str_date_parser(current_date)
    sprint_festival_dates = pd.to_datetime(['1996-02-19', '1997-02-07', '1998-01-28', '1999-02-16',
                                            '2000-02-05', '2001-01-24', '2002-02-12', '2003-02-01',
                                            '2004-01-22', '2005-02-09', '2006-01-29', '2007-02-18',
                                            '2008-02-07', '2009-01-26', '2010-02-14', '2011-02-03',
                                            '2012-01-23', '2013-02-10', '2014-01-31', '2015-02-19',
                                            '2016-02-08', '2017-01-28', '2018-02-16', '2019-02-05',
                                            '2020-01-25', '2021-02-12', '2022-02-01', '2023-01-22',
                                            '2024-02-10', '2025-01-29', '2026-02-17', '2027-02-06',
                                            '2028-01-26', '2029-02-13', '2030-02-03', '2031-01-23'])
    if flag == 'previous':
        return sprint_festival_dates[sprint_festival_dates <= current_date][-1]
    elif flag == 'next':
        return sprint_festival_dates[sprint_festival_dates > current_date][0]
    else:
        raise AssertionError


def phaser(total_length, start_value, end_value, method='linear', flip_flag=False, cfg=None):
    if cfg is not None:
        assert isinstance(cfg, dict)
    if method == 'linear':
        x = np.linspace(start_value, end_value, total_length)
    elif method == 'sigmoid':
        cfg = dict() if cfg is None else cfg
        boundary = cfg.get('boundary', 6)
        steps = np.linspace(-boundary, boundary, total_length)
        steps[0], steps[-1] = -np.inf, np.inf
        x = np.array([expit(i) for i in steps]) * (end_value - start_value) + start_value
    else:
        raise NotImplementedError
    if flip_flag:
        x = np.flipud(x)
    return x


def sigmoid_phaser(total_length, ease_length, start_value, end_value, method='ease-in', boundary=6):
    ease = phaser(ease_length, start_value, end_value, method='sigmoid', cfg={'boundary': boundary})
    if method == 'ease-in':
        const = np.full(total_length - ease_length, end_value, dtype='float')
        res = np.hstack([ease, const])
    elif method == 'ease-out':
        const = np.full(total_length - ease_length, start_value, dtype='float')
        res = np.hstack([const, ease])
    else:
        raise NotImplementedError
    return res


class SpringFestivalPhaser:
    # given input date, return weight scale coef if date is within spring festival period
    # otherwise, return 1 for rest of year
    def __init__(self, pre_weight=1.5, pre_total_length=30, pre_ease_length=15, pre_out_length=10,
                 after_weight=0.2, after_total_length=20, after_ease_length=10, _const=1):
        if pre_total_length != 0:
            pre_phaser = sigmoid_phaser(pre_total_length, pre_ease_length, _const, pre_weight, method='ease-in')
        else:
            pre_phaser = np.array([])
        if pre_out_length != 0:
            pre_out_phaser = sigmoid_phaser(pre_out_length, pre_out_length, pre_weight, after_weight, method='ease-out')
        else:
            pre_out_phaser = np.array([])
        self.pre_phaser = np.hstack([pre_phaser, pre_out_phaser])
        self.after_phaser = sigmoid_phaser(after_total_length, after_ease_length, after_weight, _const, method='ease-out')
        self.pre_total_length = pre_total_length + pre_out_length
        self.after_total_length = after_total_length
        self._const = _const

    def fit(self, current_date):
        current_date = IO.str_date_parser(current_date)
        prev_sf = get_spring_festival_date(current_date, flag='previous')
        next_sf = get_spring_festival_date(current_date, flag='next')
        prev_day_num = len(tdt.get_trading_date_range(prev_sf, current_date))
        next_day_num = len(tdt.get_trading_date_range(current_date, next_sf))
        if prev_day_num <= self.after_total_length:
            # just after the spring festival
            return self.after_phaser[prev_day_num - 1]
        elif next_day_num <= self.pre_total_length:
            # incoming spring festival
            return self.pre_phaser[self.pre_total_length - next_day_num]
        else:
            return self._const


class ReportPeriodPhaser:
    # given input date, return weight scale coef if date is within report period
    # otherwise, return 1 for rest of year
    def __init__(self, report_month, report_day, period_weight=0.2, pre_total_length=30, pre_ease_length=10,
                 after_total_length=10, after_ease_length=10, _const=1):
        self.report_month = int(report_month)
        self.report_day = int(report_day)
        self.pre_phaser = sigmoid_phaser(pre_total_length, pre_ease_length, _const, period_weight, method='ease-in')
        self.after_phaser = sigmoid_phaser(after_total_length, after_ease_length, period_weight, _const, method='ease-out')
        self.pre_total_length = pre_total_length
        self.after_total_length = after_total_length
        self._const = _const

    def fit(self, current_date):
        current_date = IO.str_date_parser(current_date)
        prev_dt = pd.Timestamp(current_date.year-1, self.report_month, self.report_day)
        curr_dt = pd.Timestamp(current_date.year, self.report_month, self.report_day)
        next_dt = pd.Timestamp(current_date.year+1, self.report_month, self.report_day)
        if prev_dt <= current_date <= curr_dt:
            prev_day_num = len(tdt.get_trading_date_range(prev_dt, current_date))
            next_day_num = len(tdt.get_trading_date_range(current_date, curr_dt))
        else:
            prev_day_num = len(tdt.get_trading_date_range(curr_dt, current_date))
            next_day_num = len(tdt.get_trading_date_range(current_date, next_dt))
        if prev_day_num <= self.after_total_length:
            # just after the report deadline
            return self.after_phaser[prev_day_num - 1]
        elif next_day_num <= self.pre_total_length:
            # incoming report deadline
            return self.pre_phaser[self.pre_total_length - next_day_num]
        else:
            return self._const


def continuous_groupby(x, method='cumcount', by=None):
    if by is None:
        assert isinstance(x, pd.Series)
        grouped = x.groupby((x != x.shift()).cumsum())
    else:
        _x = x[by]
        grouped = x.groupby((_x != _x.shift()).cumsum())
    if callable(method):
        return grouped.apply(method)
    else:
        return getattr(grouped, method)()


def common_index_extractor(base):
    if isinstance(base, dict):
        all_indexes = [v.index for k, v in base.items()]
    elif isinstance(base, Iterable):
        all_indexes = [v.index for v in base]
    else:
        raise NotImplementedError
    indexes = all_indexes[0]
    for _index in all_indexes:
        indexes = indexes.union(_index)
    return indexes.unique()


def pinyin(x, style='NORMAL', join_str='', strict_AZ=True):
    try:
        import pypinyin as ppy
    except:
        return x
    res = join_str.join([item for item in flatten_nested_lst(ppy.pinyin(x, style=getattr(ppy.Style, style)))])
    if strict_AZ:
        res = re.sub('[^A-Za-z]', '', res)
    return res


def concurrent_apply_func(func, input_list, max_workers, logger=None, debug_mode=False,
                          process_type='multiprocess', logger_callback=None,
                          collect_results=True, void_log_flag=False, **kwargs):
    # apply func to input list as first argument in a concurrent way
    assert callable(func)
    assert isinstance(max_workers, int)
    assert isinstance(input_list, list) or isinstance(input_list, tuple)
    total_jobs = len(input_list)
    result_collector = dict()
    if process_type == 'multithread':
        _executor = concurrent.futures.ThreadPoolExecutor
    elif process_type == 'multiprocess':
        _executor = concurrent.futures.ProcessPoolExecutor
    else:
        raise NotImplementedError
    if logger is None:
        logger = add_file_logger('concurrent', void_flag=void_log_flag)  # dummy logger to stream to screen
    if debug_mode:
        # pdb into func source code should work
        for _file in input_list:
            data = func(_file, **kwargs)
            if data is not None and collect_results:
                try:
                    result_collector[_file] = data
                except TypeError:
                    result_collector[pd.Timestamp.now()] = data
    else:
        with _executor(max_workers=max_workers) as executor:
            future_dict = {executor.submit(func, _file, **kwargs): _file \
                                           for _file in input_list}
            logger.info('executor submit finish')
            for _future in concurrent.futures.as_completed(future_dict):
                _file = future_dict[_future]
                current_job = input_list.index(_file) + 1
                try:
                    data = _future.result()
                except concurrent.futures.process.BrokenProcessPool:
                    return result_collector
                except Exception as _exp:
                    logger.warning('worker raised %s' % _exp)
                    data = None
                del future_dict[_future]
                del _future
                # load results into collector
                if data is not None and collect_results:
                    try:
                        result_collector[_file] = data
                    except TypeError:
                        result_collector[pd.Timestamp.now()] = data
                if logger_callback is not None:
                    assert callable(logger_callback)
                    msg = logger_callback(_file, data)
                    if data is not None:
                        logger.info('%d/%d - %s' % (current_job, total_jobs, msg))
                    else:
                        logger.warning('%d/%d - %s' % (current_job, total_jobs, msg))
                else:
                    logger.info('%d/%d - processed' % (current_job, total_jobs))
        logger.info('executor finished')
    if collect_results:
        return result_collector


def max_icir_analytical(IC_mean, IC_cov):
    assert min(IC_mean) >= 0
    IC_cov = np.array(IC_cov)
    IC_mean = np.array(IC_mean)
    IC_weight = np.dot(np.linalg.inv(IC_cov), IC_mean)
    return list(IC_weight / IC_weight.sum())


def max_icir_numeric(IC_mean, IC_cov):
    with warnings.catch_warnings():
        warnings.simplefilter('error', category=RuntimeWarning)
        IC_cov = np.array(IC_cov)
        IC_mean = np.array(IC_mean)
        factor_num = len(IC_mean)
        objective_function = lambda w: -1 * np.dot(w, IC_mean) / np.sqrt(np.dot(np.dot(w, IC_cov), w.T))
        w0 = [1.0 / factor_num] * factor_num
        bnds = [(0, 1, ) for i in range(factor_num)]
        cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        opt_result = optimize.minimize(objective_function, w0, bounds=bnds, constraints=cons)
        IC_weight_optimal = opt_result.x
        return list(IC_weight_optimal)


def retrieve_index_minute(ticker):
    ticker = ticker.split('.')[0]
    file_path = [item for item in os.listdir(ionc.minute_per_index_path) if ticker in item]
    assert len(file_path) == 1
    data = pd.read_pickle(os.path.join(ionc.minute_per_index_path, file_path[0]), compression='gzip')
    data = data.reset_index()
    data['dt'] = data['dt'] * 10000 + data['minute']
    data['dt'] = pd.to_datetime(data['dt'], format='%Y%m%d%H%M')
    data = data.set_index('dt').drop(columns=['Ticker', 'minute'])
    return data


def kelly_position(E_ret, E_std, cost):
    assert cost >= 0 and E_std > 0
    _E_ret = abs(E_ret)
    lose_chance = scipy.stats.norm.cdf(cost, loc=_E_ret, scale=E_std)
    win_chance = 1 - lose_chance
    def win_exp_helper(x):
        if x >= cost:
            return x - cost
        else:
            return 0
    def lose_exp_helper(x):
        if x <= cost:
            return x - cost
        else:
            return 0
    win_exp = scipy.stats.norm.expect(win_exp_helper, loc=_E_ret, scale=E_std)
    lose_exp = scipy.stats.norm.expect(lose_exp_helper, loc=_E_ret, scale=E_std)
    wl_ratio = win_exp / abs(lose_exp)
    kelly = (wl_ratio * win_chance - lose_chance) / wl_ratio
    if E_ret >= 0:
        return kelly
    else:
        return - kelly


def dict_key_transformer(per_asset_dict, column_index_name='Ticker'):
    # transform per asset dict of DataFrames to per feature dict of DataFrames
    per_feature_dict = dict()
    tickers = list(per_asset_dict.keys())
    assert np.all([isinstance(per_asset_dict[ticker], pd.DataFrame) for ticker in tickers])
    features = list(set(flatten_nested_lst([per_asset_dict[ticker].columns.to_list() for ticker in tickers])))
    for feature in features:
        feature_list = list()
        for ticker in tickers:
            feature_per_asset = per_asset_dict[ticker][feature]
            feature_per_asset.name = ticker
            feature_list.append(feature_per_asset)
        feature_pd = pd.concat(feature_list, axis=1)
        feature_pd.columns.name = column_index_name
        per_feature_dict[feature] = feature_pd
    return per_feature_dict


def pd_time_filter(pd_data, begin_of_time, end_of_time):
    # strip pd.Series or pd.DataFrame time range outside designated scope
    assert np.any([isinstance(pd_data, item) for item in [pd.Series, pd.DataFrame]])
    assert begin_of_time is None or isinstance(begin_of_time, dt.time)
    assert end_of_time is None or isinstance(end_of_time, dt.time)
    pd_data = pd_data.copy()  # always return a copy
    if isinstance(pd_data.index, pd.core.index.MultiIndex):
        ref_index = pd_data.index.get_level_values(level=0)
    else:
        ref_index = pd_data.index
    assert isinstance(ref_index, pd.DatetimeIndex)
    ref_time = pd.Series(ref_index.time, index=pd_data.index)
    if begin_of_time is not None:
        pd_data = pd_data.drop(ref_time.loc[ref_time < begin_of_time].index)
    if end_of_time is not None:
        pd_data = pd_data.drop(ref_time.loc[ref_time > end_of_time].index)
    return pd_data


def np_roller(data, window):
    # convert [1, 2, 3, 4] with window 2
    # to [[1, 2, 3],
    #      2, 3, 4]]
    assert isinstance(data, np.ndarray) and len(data.shape) == 1
    shape = (window, data.size - window + 1)
    strides = (data.strides[-1], data.strides[-1])
    res = np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)
    return np.array(res)


def chunk_shuffler(x, *args, groupby='date', sample_num=None):
    assert isinstance(x, pd.Series) or isinstance(x, pd.DataFrame)
    assert isinstance(x.index, pd.DatetimeIndex)
    grouped = x.groupby(getattr(x.index, groupby))
    group_keys = list(grouped.groups.keys())
    sample_num = len(group_keys) if sample_num is None else int(sample_num)
    mixed = np.random.choice(group_keys, size=sample_num, replace=False)
    shuffled = pd.concat([grouped.get_group(k) for k in mixed], axis=0, sort=False)
    res = list()
    for item in args:
        assert isinstance(item, pd.Series) or isinstance(item, pd.DataFrame)
        pd.testing.assert_index_equal(item.index, x.index)
        res.append(item.reindex(shuffled.index))
    if len(res) == 0:
        return shuffled
    else:
        return [shuffled] + res


def zipper(archive_list=[], zfile_name='default.zip', nparts=1, compression=zipfile.ZIP_DEFLATED):
    assert isinstance(archive_list, list)
    total_num = len(archive_list)
    counter = 0
    file_name = os.path.splitext(os.path.basename(zfile_name))[0]
    for chunk in tqdm(chunks(archive_list, n=int(total_num // nparts) + 1), total=nparts):
        if counter == 0:
            chunk_name = zfile_name
        else:
            chunk_name = zfile_name.replace(file_name, file_name + f'_{counter}')
        with zipfile.ZipFile(chunk_name, 'w', compression=compression) as zout:
            for item in chunk:
                print('writing: ', item)
                zout.write(item)
        counter += 1


def folder_zipper(dir_name, output_filename):
    shutil.make_archive(os.path.splitext(output_filename)[0], 'zip', dir_name)


def unzipper(zfile_name, output_path=None, passwd=None):
    if output_path is None:
        output_path = os.path.join(os.path.dirname(zfile_name), os.path.splitext(zfile_name)[0])
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with zipfile.ZipFile(zfile_name, 'r') as zin:
        zin.extractall(output_path, pwd=passwd)


def retrieve_st_stocks_range(start_date, end_date):
    collector = list()
    for trading_day in tdt.get_trading_date_range(start_date, end_date):
        st_stocks = retrieve_st_stocks(trading_day)
        collector.append(pd.Series(True, index=pd.MultiIndex.from_product([[trading_day], st_stocks], names=['dt', 'Ticker'])))
    return pd.concat(collector)


def slot_even_filler(slots, total_quota):
    # given slot quotas in ascending list and total quota,
    # try to fill each and every slot in a most possibly even form
    assert isinstance(slots, list) and slots == sorted(slots)
    if total_quota >= sum(slots):
        return slots
    n_slots = len(slots)
    even_quota = total_quota / n_slots
    if even_quota > slots[0]:
        left_overs = slot_even_filler([item - slots[0] for item in slots[1:]], total_quota - slots[0] * n_slots)
        return [slots[0] + item for item in [0] + left_overs]
    else:
        return [even_quota] * n_slots


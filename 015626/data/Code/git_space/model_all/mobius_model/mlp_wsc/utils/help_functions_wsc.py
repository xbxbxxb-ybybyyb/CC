import time
import torch
import pickle
import random
import numpy as np
import pandas as pd
from itertools import product
from bisect import bisect_left
from collections import Iterable
from multiprocessing import Pool


def multiprocessing_helper(func, max_workers, error_callback, *args, **kwargs):
    assert callable(func)
    list_all = list()
    for arg in args:
        assert isinstance(arg, Iterable)
        list_all.append(arg)
    pool = Pool(processes=max_workers)
    for i_param in product(*list_all):
        pool.apply_async(func, args=i_param, error_callback=error_callback, kwds=kwargs)
        time.sleep(0.5)
    pool.close()
    pool.join()


def expanding_helper(start_date, end_date, frequency='quarterly', time_mode='start'):
    assert frequency in ['monthly', 'quarterly', 'half_yearly', 'yearly']
    assert time_mode in ['start', 'end']
    if frequency == 'monthly':
        suffix_list = ['0101', '0201', '0301', '0401', '0501', '0601', '0701', '0801', '0901' '1001', '1101', '1201']
    elif frequency == 'quarterly':
        suffix_list = ['0101', '0401', '0701', '1001']
    elif frequency == 'half_yearly':
        suffix_list = ['0101', '0701']
    elif frequency == 'yearly':
        suffix_list = ['0101']
    else:
        raise NotImplementedError
    result_list = [str(i) + j for i in range(int(start_date[:4]), int(end_date[:4]) + 2) for j in suffix_list]
    result_list[-1] = end_date
    result_list = result_list[bisect_left(result_list, start_date): bisect_left(result_list, end_date) + 1]
    result_list = [pd.Timestamp(i) for i in result_list]
    result_list = list(zip(result_list[:-1], result_list[1:]))
    if time_mode == 'end':
        result_list = [(i[0], i[1] - pd.DateOffset(days=1)) if
                       i[1] != pd.Timestamp(end_date) else i for i in result_list]
    return result_list


def torch_seed_set(seed=7718, need_accuracy=False):
    assert isinstance(seed, int)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # for multi-gpu
    if need_accuracy:
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True


def replace_zero(data, threshold=1e-8, x=np.nan):
    assert isinstance(data, (torch.Tensor, pd.Series, pd.DataFrame, np.ndarray, int, float, np.int64,
                             np.float32)), 'the data structure of input is illegal'
    if isinstance(data, torch.Tensor):
        data = data.clone()
        data[abs(data) < threshold] = x
    elif isinstance(data, (pd.Series, pd.DataFrame)):
        data = data.copy()
        data[abs(data) < threshold] = x
    elif isinstance(data, np.ndarray):
        data = data + 0.  # 下述转化对int类型的ndarray无效，因此事先将数据类型转为float
        data = data.copy()
        data[abs(data) < threshold] = x
    else:
        if np.isclose(data, 0, atol=threshold):
            data = x
    return data


def cv_split_helper(data, n=5):
    # 交叉验证模型的损失函数，对任意给定数据集，均匀分成n份，其中n-1份拼接后成为数据集，1份留作验证集
    assert isinstance(n, int)
    cv_list_train = []
    cv_list_test = []
    if n > 1:
        split_mask = np.arange(0, data.shape[0], data.shape[0] // n + 1)
        split_mask = np.append(split_mask, data.shape[0])
        data_range_all = np.arange(data.shape[0])
        for i in range(len(split_mask) - 1):
            cv_list_train.append(np.setdiff1d(data_range_all, np.arange(split_mask[i], split_mask[i + 1]),
                                              assume_unique=True))
            cv_list_test.append(np.arange(split_mask[i], split_mask[i + 1]))
    else:
        cv_list_train.append(np.arange(data.shape[0]))
        cv_list_test.append(np.arange(data.shape[0]))
    return cv_list_train, cv_list_test


def save_pickle(save_dict, save_path, protocol_level='highest'):
    assert protocol_level in ['highest', 'default']
    protocol = pickle.HIGHEST_PROTOCOL if protocol_level == 'highest' else pickle.DEFAULT_PROTOCOL
    with open(save_path, 'wb') as temp_input:
        pickle.dump(save_dict, temp_input, protocol=protocol)
    return

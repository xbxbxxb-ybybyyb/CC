"""Utilities that are required by gplearn.
Most of these functions are slightly modified versions of some key utility
functions from scikit-learn that gplearn depends upon. They reside here in
order to maintain compatibility across different versions of scikit-learn.
"""

import re
import numbers

import numpy as np
from joblib import cpu_count


def check_random_state(seed):
    """Turn seed into a np.random.RandomState instance
    Parameters
    ----------
    seed : None | int | instance of RandomState
        If seed is None, return the RandomState singleton used by np.random.
        If seed is an int, return a new RandomState instance seeded with seed.
        If seed is already a RandomState instance, return it.
        Otherwise raise ValueError.
    """
    if seed is None or seed is np.random:
        return np.random.mtrand._rand
    if isinstance(seed, (numbers.Integral, np.integer)):
        return np.random.RandomState(seed)
    if isinstance(seed, np.random.RandomState):
        return seed
    raise ValueError('%r cannot be used to seed a numpy.random.RandomState'
                     ' instance' % seed)


def _get_n_jobs(n_jobs):
    """Get number of jobs for the computation.
    This function reimplements the logic of joblib to determine the actual
    number of jobs depending on the cpu count. If -1 all CPUs are used.
    If 1 is given, no parallel computing code is used at all, which is useful
    for debugging. For n_jobs below -1, (n_cpus + 1 + n_jobs) are used.
    Thus for n_jobs = -2, all CPUs but one are used.
    Parameters
    ----------
    n_jobs : int
        Number of jobs stated in joblib convention.
    Returns
    -------
    n_jobs : int
        The actual number of jobs as positive integer.
    """
    if n_jobs < 0:
        return max(cpu_count() + 1 + n_jobs, 1)
    elif n_jobs == 0:
        raise ValueError('Parameter n_jobs == 0 has no meaning.')
    else:
        return n_jobs


def _partition_estimators(n_estimators, n_jobs):
    """Private function used to partition estimators between jobs."""
    # Compute the number of jobs
    n_jobs = min(_get_n_jobs(n_jobs), n_estimators)

    # Partition estimators between jobs
    n_estimators_per_job = (n_estimators // n_jobs) * np.ones(n_jobs,
                                                              dtype=np.int)
    n_estimators_per_job[:n_estimators % n_jobs] += 1
    starts = np.cumsum(n_estimators_per_job)

    return n_jobs, n_estimators_per_job.tolist(), [0] + starts.tolist()


def get_y(str_list):
    temp_list_1 = []
    temp_list_2 = []
    for i, i_str in enumerate(str_list):
        if i_str == '(':
            temp_list_1.append(i)
        elif i_str == ')':
            temp_list_2.append((temp_list_1[-1], i))
            temp_list_1.pop()
    return sorted(temp_list_2)


def get_program(factor_formula, function_map, feature_list):
    # 根据给定的算子字典，特征列表及公式，得到对应的Program
    all_list = re.findall('[A-Za-z_0-9]+', factor_formula)
    non_int_list = [i for i in all_list if not i.isdigit()]
    int_list = [int(i) for i in all_list if i.isdigit()]
    program = [function_map[i] if i not in feature_list else feature_list.index(i) for i in non_int_list]
    const_arity_list = [i.const_arity for i in program if not isinstance(i, int)]

    brackets_pair_list = [i[1] for i in get_y(factor_formula)]
    const_arity_list_sorted = [const_arity_list[i] for i in np.argsort(brackets_pair_list)]

    const_arity_list_sorted.insert(0, 0)
    const_arity_list_sorted = np.cumsum(const_arity_list_sorted)
    const_params_list = [np.array(int_list[const_arity_list_sorted[i]:const_arity_list_sorted[i + 1]]) for i in
                         range(len(const_arity_list_sorted) - 1)]
    const_params_list = [const_params_list[i] for i in np.argsort(np.argsort(brackets_pair_list))]
    return program, const_params_list


def get_arity(function_set):
    # 根据给定的算子列表，得到对应的参数和常参数列表
    arities = {}
    for function in function_set:
        arity = function.arity
        arities[arity] = arities.get(arity, [])
        arities[arity].append(function)

    const_arities = {}
    for function in function_set:
        _const_arity = function.const_arity
        const_arities[_const_arity] = const_arities.get(_const_arity, [])
        const_arities[_const_arity].append(function)

    return arities, const_arities


def calc_ic_np(y, y_pred, start_time, end_time):
    y_insample = y[start_time: end_time]
    y_pred_insample = y_pred[start_time: end_time]
    data_nan_ratio = np.isnan(y_pred_insample).sum() / y_insample.shape[0]
    if data_nan_ratio < 0.1:
        if y.ndim == 2:
            ic_insample = np.full(y.shape[1], np.nan)
            for i in range(y.shape[1]):
                ic_insample[i] = np.ma.corrcoef(np.ma.masked_invalid(y_insample[:, i]),
                                                np.ma.masked_invalid(y_pred_insample[:, i])).data[0, 1]
            return ic_insample
        elif y.ndim == 1:
            ic_insample = np.ma.corrcoef(np.ma.masked_invalid(y_insample),
                                         np.ma.masked_invalid(y_pred_insample)).data[0, 1]
            return np.array([ic_insample])
        else:
            raise NotImplementedError
    else:
        if y.ndim == 2:
            return np.full(y.shape[1], np.nan)
        elif y.ndim == 1:
            return np.array([np.nan])
        else:
            raise NotImplementedError


def get_data_num(raw_df, date):
    # 计算给定日期在df中是第几行
    date_index = raw_df.index.tolist()
    date_dt = raw_df.loc[date:].index[0]
    date_num = date_index.index(date_dt)
    return date_num




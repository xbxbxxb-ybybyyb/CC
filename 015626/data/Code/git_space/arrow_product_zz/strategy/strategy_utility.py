import numpy as np
import pandas as pd
import statsmodels.api as sm
import datetime as dt
import dill as pickle
from concurrent.futures import ProcessPoolExecutor as Pool
from concurrent.futures import as_completed
from multiprocessing import Process, Manager
from line_profiler import LineProfiler
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from functools import partial

import matplotlib.pyplot as plt

plt.style.use('ggplot')
import seaborn as sns

import os, time, re, copy, random, sys

sys.path.insert(0, '..')
# from multifactor.IO import IO
# from multifactor.IO.IO_enums import *
from multifactor.utility.common import resider
from support_file.cron_setting import *
from ts.utility.ts_utility import multiprocess_wrapper

disk_path_base = data_save_path
h5_factor_base = os.path.join(disk_path_base, 'factor')

seed = 2018
random.seed(seed)
np.random.seed(seed)
os.environ['PYTHONHASHSEED'] = str(seed)


def find_file(root_path=h5_factor_base, suffix='h5', file_name_only=False):
    factor_path_dict = {}
    for path, subdirs, files in os.walk(root_path):
        for name in files:
            if suffix in name:
                fac_name = name[:name.find('.')]
                factor_path_dict[fac_name] = os.path.join(path, name)
    if file_name_only:
        factor_path_dict = {fac: os.path.basename(fac).replace('.%s' % (suffix), '') for fac in factor_path_dict}
        factor_path_dict = list(factor_path_dict.values())
    return factor_path_dict


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


@static_vars(tic=dt.datetime.now())
def pprint(*args, **kwargs):
    print(('%.3fs <- prev msg: ' % (dt.datetime.now() - pprint.tic).total_seconds()).rjust(22), *args, **kwargs)
    pprint.tic = dt.datetime.now()


def save_pickle(save_dict, save_path):
    print('saving data to:\n', save_path)
    folder = os.path.dirname(save_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    if os.path.exists(save_path):
        print('remove existing one')
        os.remove(save_path)
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict, input, protocol=pickle.HIGHEST_PROTOCOL)
    return


def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict


def read_pickle_df_date(pkl_path, sdate=None, edate=None, output_format='df'):  # ,pkl_compression='gzip'):
    data = pd.read_pickle(pkl_path)  # ,compression=pkl_compression)
    if sdate is not None and edate is not None:
        if isinstance(sdate, int) and isinstance(sdate, int):
            sdate, edate = str(sdate), str(edate)
        data = data.loc[sdate:edate]
    if output_format is 'df':
        data = data
    elif output_format is 'dict':
        data = {str(parse_file_name(pkl_path)): data}
    elif output_format is 'mi':
        data = pd.DataFrame(data.stack(), columns=[str(parse_file_name(pkl_path))])
    return data


def concat_pd(dat_exist, dat_new, sort=True, verbose=True, check_date=False):
    # dat_exist = concat_pd(dat_exist,dat_new)
    type_exist = check_df_type(dat_exist)
    type_new = check_df_type(dat_new)

    if type_new != type_exist:
        print('type error')
        raise Exception
    try:
        if type_new == 'df':
            new_date_list = set(dat_new.index)
            date_list = set(dat_exist.index)
        else:
            new_date_list = set(dat_new.index.get_level_values(0))
            date_list = set(dat_exist.index.get_level_values(0))
        if check_date:
            check_date_appendable(dat_new, dat_exist)
        duplicate_list = list(date_list.intersection(new_date_list))
        duplicate_list.sort()
        if len(duplicate_list) > 0:
            if verbose:
                print('date duplicate & drop: % days - %s - %s' % (len(duplicate_list), str(duplicate_list[0]), str(duplicate_list[-1])))
            dat_exist = dat_exist.drop(duplicate_list) if type_new == 'df' else dat_exist.drop(duplicate_list, level=0)
        dat_use = dat_exist.append(dat_new)
        if sort:
            dat_use = dat_use.sort_index() if type_new == 'df' else dat_use.sort_index(level=0)
    except:
        print('concat pd failed')
        raise Exception
    return dat_use


def concat_dict(dat_dict_exist, dat_dict_new, sort=True):
    key_list_exist = list(dat_dict_exist.keys())
    key_list_new = list(dat_dict_new.keys())
    new_minus_exist = list(set(key_list_new) - set(key_list_exist))
    if len(new_minus_exist) > 0:
        print('key list wrong - new_minus_exist:%s' % (new_minus_exist))
    dat_dict_use = {}
    for k in dat_dict_exist:
        dat_dict_use[k] = concat_pd(dat_dict_exist[k], dat_dict_new[k], sort)
    return dat_dict_use


###########
"""factor update"""


def get_start_date(cdate_list, data_length):
    fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    idx = fdate_list.index(cdate_list[0]) - data_length
    min_index = max(0, idx)
    start_date = fdate_list[min_index]
    if idx < 0:
        print('Not enough data: will use first available date:', str(start_date))
    return start_date


def find_nearest_date(date, date_list):
    nearest_date = min(date_list, key=lambda x: abs(x - date) if x <= date else 100)
    return nearest_date


def get_current_date(new_date_time=18, print_info=False):
    """if current date is not pass new_date_time such as 18 (6pm)
         it will return previous trading day
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x: abs(x - current_date) if x <= current_date else 100)
    if current_hour < new_date_time and nearest_date == current_date:
        current_date_use = fdate_list[fdate_list.index(current_date) - 1]
        if print_info:
            print('Not till refresh time ' + str(new_date_time) + ':00')
            print('Use previous trading date: ' + str(current_date_use))
    elif current_hour >= new_date_time and nearest_date == current_date:
        if print_info:
            print('Right on time: ' + str(current_date))
        current_date_use = current_date
    elif nearest_date < current_date:
        current_date_use = nearest_date
    elif nearest_date > current_date:
        current_date_use = fdate_list[fdate_list.index(nearest_date) - 1]
    return current_date_use


def date_period_handler(sdate=None, edate=None, new_date_time=18, print_info=False):
    last_day = get_current_date(new_date_time, print_info)
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        if print_info:
            print('update for one day: ' + str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i <= min(edate, last_day) and i >= sdate]
        if len(cdate_list) == 0:
            print('input date not valid: %d - %d' % (sdate, edate))
            raise Exception
        else:
            sdate, edate = cdate_list[0], cdate_list[-1]
    return sdate, edate


def check_update_date(sdate=None, edate=None, use_len=None, new_date_time=20, print_info=False):
    # check_update_date(sdate=None,edate=None)
    if sdate is not None and edate is not None:
        if sdate > edate:
            print('date input error: %s - %s ' % (sdate, edate))
            raise Exception
    use_len = 0 if use_len is None else use_len
    sdate, edate = date_period_handler(sdate, edate, new_date_time, print_info)
    fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i >= sdate and i <= edate]
    idx = max(0, fdate_list.index(cdate_list[0]) - use_len)
    sdate_prev = fdate_list[idx]
    if print_info:
        print('-' * 20, '\ndata used: %d - %d ' % (sdate_prev, edate))
        print('factor data: %d - %d \ntotal count: %d' % (sdate_prev, edate, len(cdate_list)))
        print('-' * 20)
    return sdate_prev, edate, cdate_list


def check_date_appendable(dat_new, dat_exist):
    sdate, edate, cdate_list = check_update_date(20010101, 20500101)
    cdate_list_dt = [pd.Timestamp(str(i)) for i in cdate_list]
    if isinstance(dat_exist, pd.DataFrame) or isinstance(dat_exist, pd.Series):
        if isinstance(dat_exist.index, pd.MultiIndex):
            last_exist_ls = dat_exist.index.get_level_values(level=0)
            first_append_ls = dat_new.index.get_level_values(level=0)
        else:
            last_exist_ls = dat_exist.index.tolist()
            first_append_ls = dat_new.index.tolist()
    last_exist = last_exist_ls[-1]
    first_append = first_append_ls[0]
    date_diff = cdate_list_dt.index(first_append) - cdate_list_dt.index(last_exist)
    if date_diff > 1:
        print('date not consecutive %s - %s' % (last_exist, first_append))
        raise Exception
    return


def read_pickle_omni_helper(pkl_path):
    try:
        dat = read_pickle(pkl_path)
    except:
        try:
            dat = pd.read_pickle(pkl_path)
        except:
            try:
                dat = pd.read_pickle(pkl_path, compression='gzip')
            except:
                print('read existing pickle failed: %s' % (pkl_path))
                raise Exception
    return dat


def read_pickle_omni(pkl_path):
    if isinstance(pkl_path, str):
        dat = read_pickle_omni_helper(pkl_path)
    elif isinstance(pkl_path, list) or isinstance(pkl_path, dict):
        if isinstance(pkl_path, dict):
            pkl_path = list(pkl_path.values())
        tic = time.time()
        dat_list = []
        for pkl in pkl_path:
            dat_tmp = read_pickle_omni_helper(pkl)
            dat_list.append(dat_tmp)
        tsx = time.time()
        if isinstance(dat_tmp, dict):
            dat = dat_list
        else:
            dat = pd.concat(dat_list, axis=0)
        toc = time.time()
        print('load pkl list done - total %s - concat %s' % (print_time(toc, tic), print_time(toc, tsx)))
    else:
        print('pkl path problem')
        raise Exception
    return dat


# save_df2pkl

# save_df2pkl
def update_pickle(dat, pkl_path, operation='append', check_date=True, compression=False):
    tic = time.time()
    concat_time_str = ''
    if operation == 'create':
        if os.path.exists(pkl_path):
            print('file exist: remove first - %s' % (pkl_path))
            os.remove(pkl_path)
        save_pickle_omni(dat, pkl_path)
    elif operation == 'append':
        if os.path.exists(pkl_path):
            dat_exist = read_pickle_omni(pkl_path)
            if isinstance(dat_exist, dict):
                dat = concat_dict(dat_exist, dat)
            elif isinstance(dat_exist, pd.DataFrame):
                dat = concat_pd(dat_exist, dat, check_date=check_date)
            else:
                print('data type error')
                raise Exception
            toc1 = time.time()
            concat_time_str = '\n(concat used %s)' % (print_time(toc1, tic))
    save_pickle_omni(dat, pkl_path, compression)
    toc = time.time()
    print('update_pickle done %s - %s%s' % (print_time(toc, tic), pkl_path, concat_time_str))
    return


def path_check(path):
    folder = os.path.dirname(path) if path.find('.') > 0 else path
    if not os.path.exists(folder):
        print('folder not exist,create one: %s' % (folder))
        os.makedirs(folder)
    return


def save_pickle_omni(dat, pkl_path, compression=False):
    path_check(pkl_path)
    if isinstance(dat, dict):
        save_pickle(dat, pkl_path)
    elif isinstance(dat, pd.DataFrame) or isinstance(dat, pd.core.series.Series):
        if compression:
            dat.to_pickle(pkl_path, compression='gzip')
        else:
            dat.to_pickle(pkl_path)
    else:
        raise Exception
    return


# def save_dict2pkl(dat_dict, pkl_path, operation='append'):
#     if operation == 'create':
#         save_pickle(dat_dict, pkl_path)
#     elif operation == 'append':
#         try:
#             dat_dict_exist = read_pickle(pkl_path)  # ,compression=pkl_compression)
#             type_exist = check_df_type(dat_exist)
#             if type_new != type_exist:
#                 print('type error')
#                 raise Exception
#         except:
#             print('read existing pickle failed: %s' % (pkl_path))
#             dat_exist = dat
#         try:
#             if type_new == 'df':
#                 new_date_list = set(dat.index)
#                 date_list = set(dat_exist.index)
#             else:
#                 new_date_list = set(dat.index.get_level_values(0))
#                 date_list = set(dat_exist.index.get_level_values(0))
#             duplicate_list = list(date_list.intersection(new_date_list))
#             if len(duplicate_list) > 0:
#                 print('date duplicate & drop:', str(duplicate_list))
#                 dat_exist = dat_exist.drop(duplicate_list) if type_new == 'df' else dat_exist.drop(duplicate_list, level=0)
#             dat_use = dat_exist.append(dat)
#             dat_use = dat_use.sort_index() if type_new == 'df' else dat_use.sort_index(level=0)
#         except:
#             print('append error')
#         if len(dat_use) >= len(dat_exist):
#             dat_use.to_pickle(pkl_path)  # ,compression=pkl_compression)
#         else:
#             # logger.error('ticker:%s,error: data history deleted - dumping not performed' % (ticker))
#             print('data history deleted - dumping not performed')
#     return


def parse_file_name(file_name):
    fname = os.path.basename(file_name)
    name = fname[:fname.find('.')]
    return name


def func_parallel_date(func, input_list, sdate, edate, output_format='df', max_workers=10, logger=None):
    tic = time.time()
    total_job = len(input_list)
    collector = []
    print_func_info = print if logger is None else logger.info
    print_func_warning = print if logger is None else logger.warning
    print_func_info('-' * 5, ' Func Parallel Start ', '-' * 5)
    print_func_info('%d files  %s - %s ' % (len(input_list), sdate, edate))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(func, file_path, sdate, edate): file_path for file_path in input_list}
        for future in concurrent.futures.as_completed(future_to_file_list):
            file_path = future_to_file_list[future]
            try:
                data = future.result()
                collector.append(data)
            except Exception as exc:
                print_func_warning('%r generated an exception: %s' % (file_path, exc))
            else:
                print_func_info('%d/%d - %r' % (input_list.index(file_path) + 1, total_job, file_path))
        if output_format == 'df':
            print_func_info('concating results')
            data_collector = pd.concat(collector, axis=0)
        elif output_format == 'dict':
            data_collector = {}
            for d in collector:
                data_collector.update(d)
    toc = time.time()
    time_spent = (str((round((toc - tic) / 60, 2))) + ' minutes')
    print_func_info('-' * 5, ' Func Parallel End (%s) ' % (time_spent), '-' * 5)
    return data_collector


def multi_index_to_dataframe(h5_data):
    data_dict = {}
    for factor in h5_data.columns:
        data_dict[factor] = h5_data[factor].unstack()
    return data_dict


def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))


def reindex_dict(data_dict, index, column):
    data_dict_align = {}
    for fac in data_dict:
        data_dict_align[fac] = data_dict[fac].reindex(index=index, columns=column)
    return data_dict_align


def align_data(data_dict):
    i = 0
    for factor in data_dict:
        if type(data_dict[factor]) == pd.DataFrame:
            if i == 0:
                stock_list = data_dict[factor].columns.tolist()
                date_list = data_dict[factor].index.tolist()
                i = i + 1
            else:
                stock_list = np.intersect1d(stock_list, data_dict[factor].columns.tolist())
                date_list = np.intersect1d(date_list, data_dict[factor].index.tolist())
        elif type(data_dict[factor]) == pd.Series:
            if i == 0:
                date_list = data_dict[factor].index.tolist()
                i = i + 1
            else:
                date_list = np.intersect1d(date_list, data_dict[factor].index.tolist())
        elif type(data_dict[factor]) == dict:
            for fac in data_dict[factor]:
                if type(data_dict[factor][fac]) == pd.DataFrame:
                    if i == 0:
                        stock_list = data_dict[factor][fac].columns.tolist()
                        date_list = data_dict[factor][fac].index.tolist()
                        i = i + 1
                    else:
                        stock_list = np.intersect1d(stock_list, data_dict[factor][fac].columns.tolist())
                        date_list = np.intersect1d(date_list, data_dict[factor][fac].index.tolist())
                        # align dataframe and series
    data_dict_aligned = {}
    for factor in data_dict:
        # print (factor)
        if type(data_dict[factor]) == pd.DataFrame:
            data_dict_aligned[factor] = data_dict[factor][stock_list].loc[date_list]
        elif type(data_dict[factor]) == pd.Series:
            data_dict_aligned[factor] = data_dict[factor].loc[date_list]
        elif type(data_dict[factor]) == dict:
            data_dict_aligned[factor] = {}
            for fac in data_dict[factor]:
                if type(data_dict[factor][fac]) == pd.DataFrame:
                    data_dict_aligned[factor][fac] = data_dict[factor][fac][stock_list].loc[date_list]

                else:
                    data_dict_aligned[factor][fac] = data_dict[factor][fac]
    return data_dict_aligned


def align_data_outer(data_dict):
    # maybe should use dt, Ticker instead
    i = 0
    for factor in data_dict:
        if np.any([isinstance(data_dict[factor], _type) for _type in [pd.DataFrame, pd.Series]]):
            if isinstance(data_dict[factor].index, pd.core.index.MultiIndex):
                if 'dt' in data_dict[factor].index.names:
                    if i == 0:
                        date_list = list(set(data_dict[factor].index.get_level_values(level=0).tolist()))
                        i = i + 1
                    else:
                        new_list = list(set(data_dict[factor].index.get_level_values(level=0).tolist()))
                        date_list = union(date_list, new_list)
            else:
                if type(data_dict[factor]) == pd.DataFrame:
                    if i == 0:
                        stock_list = data_dict[factor].columns.tolist()
                        date_list = data_dict[factor].index.tolist()
                        i = i + 1
                    else:
                        # stock_list = np.intersect1d(stock_list, data_dict[factor].columns.tolist())
                        # date_list = np.intersect1d(date_list, data_dict[factor].index.tolist())
                        stock_list = union(stock_list, data_dict[factor].columns.tolist())
                        date_list = union(date_list, data_dict[factor].index.tolist())

                else:  # Series
                    if i == 0:
                        date_list = data_dict[factor].index.tolist()
                        i = i + 1
                    else:
                        date_list = union(date_list, data_dict[factor].index.tolist())
        elif type(data_dict[factor]) == dict:
            for nested_factor in data_dict[factor]:
                if type(data_dict[factor][nested_factor]) == pd.DataFrame:
                    if i == 0:
                        stock_list = data_dict[factor][nested_factor].columns.tolist()
                        date_list = data_dict[factor][nested_factor].index.tolist()
                        i = i + 1
                    else:
                        stock_list = union(stock_list, data_dict[factor][nested_factor].columns.tolist())
                        date_list = union(date_list, data_dict[factor][nested_factor].index.tolist())
        else:
            continue
    date_list.sort()
    stock_list.sort()
    data_dict_aligned = {}
    for factor in data_dict:
        if np.any([isinstance(data_dict[factor], _type) for _type in [pd.DataFrame, pd.Series]]):
            if isinstance(data_dict[factor].index, pd.core.index.MultiIndex):
                if 'dt' in data_dict[factor].index.names:
                    # data_dict_aligned[factor] = data_dict[factor].loc[date_list]
                    data_dict_aligned[factor] = data_dict[factor].reindex(index=date_list)

            else:
                if type(data_dict[factor]) == pd.DataFrame:
                    # data_dict_aligned[factor] = data_dict[factor].loc[date_list, stock_list]
                    data_dict_aligned[factor] = data_dict[factor].reindex(index=date_list, columns=stock_list)
                else:
                    # data_dict_aligned[factor] = data_dict[factor].loc[date_list]
                    data_dict_aligned[factor] = data_dict[factor].reindex(index=date_list)
        elif type(data_dict[factor]) == dict:
            data_dict_aligned[factor] = {}
            for nested_factor in data_dict[factor]:
                if type(data_dict[factor][nested_factor]) == pd.DataFrame:
                    # data_dict_aligned[factor][nested_factor] = data_dict[factor][nested_factor].loc[date_list, stock_list]
                    data_dict_aligned[factor][nested_factor] = data_dict[factor][nested_factor].reindex(index=date_list, columns=stock_list)
    return data_dict_aligned


def median_filter(factor_df, mad=3, winsor=False, handle_same=False):
    factor_dict = factor_df.copy()
    factor_mat = factor_dict.values
    # dm = np.nanmedian(factor_mat,axis=1)
    dm = factor_dict.median(axis=1)
    dm_median = (factor_dict.subtract(dm, axis=0)).abs().median(axis=1)
    if handle_same:
        dm_avg = (factor_dict.subtract(dm, axis=0)).abs().mean(axis=1)
        dm_median[dm_median == 0] = dm_avg
    # dm1 = np.nanmedian(abs((factor_mat.T - dm).T),axis=1)
    date_num, stock_num = factor_mat.shape
    fac_ub = pd.DataFrame(np.tile(dm + mad * dm_median.values, [stock_num, 1]).T, index=factor_dict.index, columns=factor_dict.columns)
    fac_lb = pd.DataFrame(np.tile(dm - mad * dm_median.values, [stock_num, 1]).T, index=factor_dict.index, columns=factor_dict.columns)
    if winsor:
        factor_dict[factor_dict > fac_ub] = np.nan
        factor_dict[factor_dict < fac_lb] = np.nan
    else:
        factor_dict[factor_dict > fac_ub] = fac_ub
        factor_dict[factor_dict < fac_lb] = fac_lb
    return factor_dict


def NormWinsor(factor_df, universe=None, bound=3, winsor=False, handle_same=False):
    factor_dict = factor_df.copy()
    if universe is not None:
        factor_dict = factor_dict.reindex(columns=universe.columns, index=universe.index).dropna(how='all')
        factor_dict[~universe] = np.nan
    factor_dict = median_filter(factor_dict, mad=bound, winsor=winsor, handle_same=handle_same)
    std_ts = factor_dict.std(axis=1, ddof=0)
    std_ts[std_ts == 0] = 1
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1), axis=0).divide(std_ts, axis=0)
    return factor_dict


def norm_winsor(factor_dict, universe=None, bound=3, winsor=False, handle_same=False):
    if isinstance(factor_dict, pd.DataFrame):
        factor_std = NormWinsor(factor_dict, universe, bound, winsor, handle_same)
    elif isinstance(factor_dict, dict):
        factor_std = {i: NormWinsor(factor_dict[i], universe, bound, winsor, handle_same) for i in factor_dict}
    return factor_std


def regression_ols(y, x):
    # calculate ols problem given y as DataFrame and x as dictionary with DataFrames of regressors
    assert (isinstance(x, dict))
    date_num, stock_num = y.shape
    x_list = list(x.keys())
    contains_industry = True if 'Industry' in x_list else False
    x_num = len(x_list) - 1 if contains_industry else len(x_list)
    x_mat = np.ones([x_num, date_num, stock_num])
    y_mat = np.array(y)
    r2_mat = np.empty(date_num)
    r2_mat[:] = np.nan
    beta_mat = np.empty([date_num, x_num + 1])
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
    beta = pd.DataFrame(beta_mat, columns=['intercept'] + x_list, index=y.index)
    tstats = pd.DataFrame(tstats_mat, columns=['intercept'] + x_list, index=y.index)
    return res, r2, beta, tstats


def batch_neutralize(y_dict, x):
    y_dict_residual = {}
    for fac in y_dict:
        res, _, _, _ = regression_ols(y_dict[fac], x)
        y_dict_residual[fac] = res
    return y_dict_residual


def check_key_by_value(dictionary, value):
    return (list(dictionary.keys())[list(dictionary.values()).index(value)])


def stats_model_ols(y, x, min_percentage=5):
    res = np.full_like(y, np.nan, dtype=np.double)
    mask = np.isfinite(y + x.sum(axis=1))
    if np.count_nonzero(mask) / len(mask) * 100 < min_percentage:
        raise ValueError
    ols = resider(x[mask], y[mask], method='sm.OLS', add_const=True, mean_only=False, r_square=False, return_sm=True)
    res[mask] = ols.resid
    return res, ols.rsquared, ols.params, ols.tvalues


def is_dummy(x):
    x = np.array(x) if not isinstance(x, np.ndarray) else x
    one_num = np.count_nonzero(x == 1)
    zero_num = np.count_nonzero(x == 0)
    if one_num + zero_num == x.size:
        return True
    else:
        return False


def batch_read(fac_path, sdate=None, edate=None, fac_list=None, dat_type='matrix'):
    if isinstance(fac_path, str):
        fac_list = [i[:-3] for i in os.listdir(fac_path) if i[-2:] == 'h5'] if fac_list is None else fac_list
        path_dict = {fac: os.path.join(fac_path, fac + '.h5') for fac in fac_list}
    elif isinstance(fac_path, dict):
        # fac_list = list(fac_path.values())
        path_dict = fac_path
    fac_list = list(path_dict.keys())
    sdate = 20090101 if sdate is None else sdate
    edate = 20991231 if edate is None else edate
    fac_dict = {}
    name_dict = {}
    print('loading factor:\n', str(fac_list))
    for fac in path_dict:
        print(str(fac_list.index(fac) + 1) + '/' + str(len(fac_list)) + ' --- ' + fac)
        try:
            dat_mi = IO.read_data([sdate, edate], alt=path_dict[fac])
            col = dat_mi.columns[0]
            name_dict[fac] = col
            if dat_type == 'matrix':
                fac_dict[col] = dat_mi[col].unstack()
            elif dat_type == 'mi':
                fac_dict[col] = dat_mi
        except:
            print('error')
    col_list = list(name_dict.values())
    if col_list != fac_list:
        print('h5 name list not matching column list:%s' % (name_dict))
    print('done')
    return fac_dict


def date_parser(str_name):
    if any([isinstance(str_name, dt.date), isinstance(str_name, dt.datetime), isinstance(str_name, pd.Timestamp)]):
        return pd.Timestamp(str_name)
    if type(str_name) is int:
        str_name = str(str_name)
    if type(str_name) is str:
        if len(str_name) == 8:
            return pd.Timestamp(dt.datetime.strptime(str_name, '%Y%m%d'))
        elif len(str_name) == 14:
            return pd.Timestamp(dt.datetime.strptime(str_name, '%Y%m%d%H%M%S'))
        else:
            raise AssertionError
    else:
        raise AssertionError


def print_current_time():
    return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def show_time_spent(ts):
    if ts > 60:
        time_spent = (str((round((ts) / 60, 2))) + ' minutes')
    else:
        time_spent = (str((round((ts), 2))) + ' seconds')
    return time_spent


def print_time(toc, tic, show_time=True, remain_iter=None):
    ts = toc - tic
    time_spent = show_time_spent(ts)
    if remain_iter is not None:
        time_spent_total = '/ remain %s' % (show_time_spent(ts * remain_iter))
    else:
        time_spent_total = ''
    time_str = ' (used %s%s) ' % (time_spent, time_spent_total)
    if show_time:
        time_str = time_str + '- ' + print_current_time()
    return time_str


def concat_dict_ts(data_dict):
    # data_dict = {'20160101':{'a':'b'},'20160102':{'a':'b'}}
    # check subkey
    dict_combine = {}
    fac_list = []
    date_list = list(data_dict.keys())
    date_list.sort()
    for key in date_list:
        fac_list = fac_list + list(data_dict[key].keys())
    fac_list = list(set(fac_list))
    fac_list.sort()
    for fac in fac_list:
        df_list = []
        for key in date_list:
            df_list.append(data_dict[key][fac])
        dict_combine[fac] = pd.concat(df_list, axis=0)
    return dict_combine


# def ts_pred_roll(y_pd, x_pd, model_type='ols', roll_num=60, min_pct=0.5):
#     # y: t*1 , x: t*k
#     y, x = y_pd.values, x_pd.values
#     stk_name = y_pd.name
#     date_list = y_pd.index.tolist()
#     date_num = len(y)
#     min_size = int(roll_num / 2)
#     collector_mat = np.ones([date_num, len(col_name)])
#     collector_mat[:] = np.nan
#     iter_num = date_num - roll_num + 1
#     for iter_start in range(iter_num):
#         iter_end = iter_start + roll_num
#         yt = y[iter_start:iter_end]
#         xt = x[iter_start:iter_end, :]
#         mask = np.isfinite(yt + xt.sum(axis=1))
#         if np.count_nonzero(mask) >= min_size:
#             ts_model = model_fit(yt, xt, min_size)
#             collector_mat[iter_end - 1, 0], collector_mat[iter_end - 1, 1:]
#     index_tuple = [date_list, [stk_name] * len(date_list)]
#     mi_index = pd.MultiIndex.from_tuples(list(zip(*index_tuple)), names=['dt', 'Ticker'])
#     result_mi = pd.DataFrame(collector_mat, columns=col_name, index=mi_index)
#     return result_mi


# def ts_predict(ts_y, ts_x, shrink_len=[120, 40]):
#     """
#     assume y & x are concurrent
#     1. fit:     y(t) = intcp + beta*x(t-1) + resid
#     2. predict: y(t+1) = fitt_model(t)
#     """
#     y_pred = ts_reg(ts_y, ts_x.shift(1))
#
#     if shrink_len is not None:
#         for roll_num in shrink_len:
#             y_pred = y_pred + y_pred.rolling(roll_num).mean()
#     return y_pred


def remove_dict_check(remove_priority, dict_member, min_num=1):
    """
    remove by priority list
    if min_num>1: min_num is int
    if min_num is percentage: will do a check of factor number in each group
    """
    if min_num >= 1:
        min_dict = {k: min_num for k in dict_member}
    elif min_num < 1 and min_num > 0:
        min_dict = {k: max(1, int(min_num * len(dict_member[k]))) for k in dict_member}
    remove_ind = True
    for remove_name in remove_priority:
        try_index = 0
        while remove_ind and try_index < len(remove_priority):
            try_index = try_index + 1
            for grp_name in dict_member:
                if remove_name in dict_member[grp_name] and len(dict_member[grp_name]) > min_dict[grp_name]:
                    dict_member[grp_name].remove(remove_name)
                    remove_ind = False
    return dict_member


def dict_slicer(factor_tank, sdate, edate):
    sdate, edate = date_parser(sdate), date_parser(edate)
    factor_tank_sliced = {}
    for fac in factor_tank:
        if isinstance(factor_tank[fac], pd.DataFrame) or isinstance(factor_tank[fac], pd.Series):
            factor_tank_sliced[fac] = factor_tank[fac].loc[sdate:edate]
        if isinstance(factor_tank[fac], dict):
            factor_tank_sliced[fac] = {}
            for sub in factor_tank[fac]:
                if isinstance(factor_tank[fac][sub], pd.DataFrame) or isinstance(factor_tank[fac][sub], pd.Series):
                    factor_tank_sliced[fac][sub] = factor_tank[fac][sub].loc[sdate:edate]
    return factor_tank_sliced


def score2label(y, label_cut):
    """
    Input:
    label_cut: (list) [0.7,0.3] 
    Output:
        label based on label cut: [1,-1]
         1: top 30% ranked stocks
        -1: bottom 30% ranked stocks
    """
    if isinstance(label_cut, np.float):
        label_cut = [label_cut, 1 - label_cut]
    elif isinstance(label_cut, list):
        if len(label_cut) != 2:
            raise Exception
    label_cut.sort()
    if isinstance(y, pd.DataFrame) or isinstance(y, pd.Series):
        if isinstance(y.index, pd.MultiIndex):
            y_use = y.unstack()
        else:
            y_use = y
        y_label = pd.DataFrame(np.full_like(y_use, fill_value=np.nan), index=y_use.index, columns=y_use.columns)
        y_top = y_use.quantile(q=label_cut[1], axis=1)
        y_bottom = y_use.quantile(q=label_cut[0], axis=1)
        top_mask = y_use.subtract(y_top, axis=0) >= 0
        bottom_mask = y_use.subtract(y_bottom, axis=0) <= 0
        y_label[top_mask] = 1
        y_label[bottom_mask] = -1
        if isinstance(y.index, pd.MultiIndex):
            y_label = y_label.stack()
    return y_label


def dict_df2_dict_mat(x_dict, aligned=False):
    if not isinstance(x_dict, dict):
        raise AssertionError
    if aligned:
        x_algn = x_dict
    else:
        x_algn = align_data_outer(x_dict)
    x_list = list(x_dict.keys())
    x_list.sort()
    row_num, col_num = x_algn[x_list[0]].shape
    df_index, df_column = x_algn[x_list[0]].index, x_algn[x_list[0]].columns

    fac_num = len(x_algn.keys())
    x_mat = np.ones([fac_num, row_num, col_num])
    x_mat[:] = np.nan
    mat_dict = {}
    for fac in x_list:
        x_mat[x_list.index(fac), :, :] = x_algn[fac].values
    mat_dict['value'] = x_mat
    mat_dict['key'] = x_list
    mat_dict['index'] = df_index.tolist()
    mat_dict['column'] = df_column.tolist()
    return mat_dict


def slice_mat_dict(x_dict_mat, sdate, edate, collapse=True, value_only=True):
    sdate = date_parser(sdate)
    edate = date_parser(edate)
    # start_idx = x_dict_mat['index'].index(sdate)
    # end_idx = x_dict_mat['index'].index(edate)+1
    index_ind = [True if i >= sdate and i <= edate else False for i in x_dict_mat['index']]
    x_value = x_dict_mat['value'][:, index_ind, :]
    if value_only:
        if collapse:
            if len(x_value.shape) == 3:
                # remain factor_type, append another day to the right
                x_value = x_value.reshape((x_value.shape[0], x_value.shape[1] * x_value.shape[2]))
            elif len(x_value.shape) == 2:
                x_value = x_value.reshape((1, x_value.shape[0] * x_value.shape[1]))
        return x_value
    else:
        x_dict_mat_current = {}
        x_dict_mat_current['index'] = list(np.array(x_dict_mat['index'])[index_ind])
        x_dict_mat_current['column'] = x_dict_mat['column']
        x_dict_mat_current['value'] = x_value
        x_dict_mat_current['key'] = x_dict_mat['key']
        return x_dict_mat_current


def combine_mat_dict(dict_mat1, dict_mat2):
    # checking
    if dict_mat1['index'] != dict_mat2['index'] or dict_mat1['column'] != dict_mat2['column']:
        print('index/columns not matching')
        raise Exception
    comb_dict_mat = {}
    comb_dict_mat['index'], comb_dict_mat['column'] = dict_mat1['index'], dict_mat1['column']
    comb_dict_mat['key'] = dict_mat1['key'] + dict_mat2['key']
    # date_num,stk_num,fac_num = len(comb_dict_mat['index']),len(comb_dict_mat['column']),len(comb_dict_mat['key'])
    comb_dict_mat['value'] = np.vstack([dict_mat1['value'], dict_mat2['value']])
    return comb_dict_mat


def slice_collapse_prep(dat, sdate, edate, drop_y_nan=True, fill_x_nan=True):
    y_train = slice_mat_dict(dat['y_dict_mat'], sdate, edate, collapse=True)
    x_train = slice_mat_dict(dat['x_dict_mat'], sdate, edate, collapse=True)
    if drop_y_nan:
        y_train_mask = np.isfinite(y_train)[0]
        y_train = y_train[:, y_train_mask].T.ravel()
        x_train = x_train[:, y_train_mask].T
    if fill_x_nan:
        x_train[np.isnan(x_train)] = 0
    x_df = pd.DataFrame(x_train, columns=dat['x_dict_mat']['key'])
    y_df = pd.DataFrame(y_train, columns=['y'])
    return y_df, x_df


def get_lineage(tree, feature_names):
    left = tree.tree_.children_left
    right = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features = [feature_names[i] for i in tree.tree_.feature]
    # get ids of child nodes
    idx = np.argwhere(left == -1)[:, 0]
    node_list = []

    def recurse(left, right, child, lineage=None):
        if lineage is None:
            lineage = [child]
        if child in left:
            parent = np.where(left == child)[0].item()
            split = 'l'
        else:
            parent = np.where(right == child)[0].item()
            split = 'r'
        lineage.append((parent, split, threshold[parent], features[parent]))
        if parent == 0:
            lineage.reverse()
            return lineage
        else:
            return recurse(left, right, parent, lineage)

    for child in idx:
        child_list = []
        for node in recurse(left, right, child):
            child_list.append(node)
        node_list.append(child_list)
    return node_list


def excel_saver(output_dict, excel_name):
    writer = pd.ExcelWriter(excel_name, engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer, sheet_name=key)
    writer.save()
    return


def show_status_bar(i, n, show_num=50):
    # n = 100
    # show_num = 50
    divisor = int(n / show_num)
    # for i in range(n):
    if i % divisor == 0:
        pct = (i + 1) / n
        done_num = int(pct * show_num)
        undone_num = show_num - done_num
        pct_round = int(pct * 100)
        pct_str = (3 - len(str(pct_round))) * ' ' + str(pct_round) + '%'
        show_str = '|' + '*' * done_num + ' ' * undone_num + '|' + '%s done' % (pct_str)
    else:
        show_str = None
    return show_str


def winsorized_mean(x, cut_range=(5, 95)):
    x = np.ma.masked_invalid(x)
    x = x.data[~x.mask]
    l_b = np.percentile(x, cut_range[0])
    u_b = np.percentile(x, cut_range[1])
    return np.mean(x[(x >= l_b) & (x <= u_b)])


def df_formatter(dataframe, factor_name):
    data_MI = pd.DataFrame(dataframe.stack(), columns=[factor_name])
    data_MI.index.names = ['dt', 'Ticker']
    data_MI = data_MI.dropna()
    return data_MI


def calc_ic_stats(IC_ts):
    IC_mean = IC_ts.mean()
    IC_std = IC_ts.std()
    ICIR = IC_mean / IC_std  # *np.sqrt(240)
    IC_stats = pd.DataFrame([IC_mean, IC_std, ICIR], index=['IC_mean', 'IC_std', 'ICIR'])
    return IC_stats


def get_split_list(iter_list, max_block=5):
    list_curr = []
    list_split = []
    for i in iter_list:
        list_curr.append(i)
        if len(list_curr) == max_block:
            list_split.append(list_curr)
            list_curr = []
        else:
            if iter_list.index(i) == (len(iter_list) - 1):
                list_split.append(list_curr)
    return list_split


def dict2mi_helper(col, df_dict, sdate=None, edate=None, alpha_universe_mi=None):
    if sdate is not None and edate is not None:
        if isinstance(sdate, int):
            sdate_dt = pd.Timestamp(str(sdate))
            edate_dt = pd.Timestamp(str(edate))
        else:
            raise Exception
        slice_date = True
    else:
        slice_date = False
    obj_mi = df_dict[col].stack() if not isinstance(df_dict[col].index, pd.MultiIndex) else df_dict[col]
    if alpha_universe_mi is not None:
        obj_mi = obj_mi.reindex(index=alpha_universe_mi.index)
    obj_mi = obj_mi.loc[sdate_dt:edate_dt] if slice_date else obj_mi
    obj_mi = pd.DataFrame(obj_mi, columns=[col])
    if col == 'Industry':
        obj_mi = pd.get_dummies(obj_mi['Industry'])
        obj_mi.columns = [int(i) for i in obj_mi.columns.tolist()]
    return obj_mi


def dict2mi(df_dict, col_list=None, sdate=None, edate=None,
            alpha_universe_mi=None, verbose=False, parallel=False):
    tic = time.time()
    if col_list is None:
        if isinstance(df_dict, pd.DataFrame):
            col_list = df_dict.columns.tolist()
        elif isinstance(df_dict, dict):
            col_list = list(df_dict.keys())
    if sdate is not None and edate is not None:
        if isinstance(sdate, int):
            sdate_dt = pd.Timestamp(str(sdate))
            edate_dt = pd.Timestamp(str(edate))
        else:
            raise Exception
        slice_date = True
        if verbose:
            print('slice date %s - %s' % (str(sdate), str(edate)))
    else:
        slice_date = False
    if alpha_universe_mi is not None:
        if not isinstance(alpha_universe_mi.index, pd.MultiIndex):
            if verbose:
                print('stack alpha_universe to mi format')
            alpha_universe_mi = alpha_universe_mi.stack()
            alpha_universe_mi = alpha_universe_mi[alpha_universe_mi]
        if slice_date:
            alpha_universe_mi = alpha_universe_mi.loc[sdate_dt:edate_dt]

    if parallel:
        use_dict = multiprocess_wrapper(func=dict2mi_helper, iter_list=col_list,
                                        df_dict=df_dict, sdate=sdate, edate=edate,
                                        alpha_universe_mi=alpha_universe_mi, collect_output=True)
    else:
        use_dict = {}
        col_name = []
        col_num = len(col_list)
        for col in col_list:
            try:
                tic1 = time.time()
                obj_mi = df_dict[col].stack() if not isinstance(df_dict[col].index, pd.MultiIndex) else df_dict[col]
                if alpha_universe_mi is not None:
                    obj_mi = obj_mi.reindex(index=alpha_universe_mi.index)
                use_dict[col] = obj_mi.loc[sdate_dt:edate_dt] if slice_date else obj_mi
                if col == 'Industry':
                    industry_mi = df_dict[col] if isinstance(df_dict[col].index, pd.MultiIndex) else df_dict[col].stack()
                    use_dict[col] = pd.get_dummies(industry_mi)
                    col_name_current = [int(i) for i in use_dict[col].columns.tolist()]
                else:
                    col_name_current = [col]
                col_name = col_name + col_name_current
                toc1 = time.time()
            except:
                print('dict2mi failed for %s' % (col))
                raise Exception
            if verbose:
                print('stack - %d/%d - %s - %s' % (col_list.index(col) + 1, col_num, col, print_time(toc1, tic1)))
    col_list = list(use_dict.keys())
    col_num = len(col_list)
    if verbose:
        toc2 = time.time()
        print('stack %d fac done - %s' % (col_num, print_time(toc2, tic)))

    mi = pd.concat(list(use_dict.values()), axis=1)
    mi.columns = col_list
    if verbose:
        toc3 = time.time()
        print('concat all fac done - %s' % (print_time(toc3, toc2)))
        print('dict2mi done ~ %s' % (print_time(toc3, tic)))
    return mi


def get_class_params(class_object, return_type='dict'):
    attrs = vars(class_object)
    class_params_dict = {k: attrs[k] for k in attrs if isinstance(attrs[k], str)
                         or isinstance(attrs[k], bool) or isinstance(attrs[k], int)
                         or isinstance(attrs[k], float)}
    if return_type == 'dict':
        return class_params_dict
    elif return_type == 'df':
        class_params_df = pd.DataFrame(list(class_params_dict.items()))
        class_params_df.columns = ['param', 'value']
        class_params_df = class_params_df.set_index('param')
        return class_params_df


def check_data_coverage(data):
    # check input type mi or dict of dataframe:
    if isinstance(data, pd.DataFrame):
        factor_coverage = np.isfinite(data).groupby(by='dt').sum()
    elif isinstance(data, dict):
        fac_list = list(data.keys())
        ls = []
        for fac in fac_list:
            ls.append(np.isfinite(data[fac]).sum(axis=1))
        factor_coverage = pd.concat(ls, axis=1)
        factor_coverage.columns = fac_list
    return factor_coverage


def check_data_std(data):
    # check input type mi or dict of dataframe:
    if isinstance(data, pd.DataFrame):
        factor_std = data.groupby(by='dt').std()
    elif isinstance(data, dict):
        fac_list = list(data.keys())
        ls = []
        for fac in fac_list:
            ls.append(data[fac].std(axis=1))
        factor_std = pd.concat(ls, axis=1)
        factor_std.columns = fac_list
    return factor_std


def factor_fillna_univ(factor_dict, uni):
    fac_list = list(factor_dict.keys())
    fac_index, fac_col = factor_dict[fac_list[0]].index, factor_dict[fac_list[0]].columns
    uni_current = uni.reindex(index=fac_index, columns=fac_col)
    uni_current = uni_current.fillna(False).astype('bool')
    for fac in fac_list:
        factor_dict[fac][uni_current] = factor_dict[fac].fillna(0)
    return factor_dict


def check_df_type(dat):
    if not isinstance(dat, pd.DataFrame):
        raise TypeError
    if isinstance(dat.index, pd.MultiIndex):
        df_type = 'mi'
    else:
        df_type = 'df'
    return df_type


def dict2df(data_dict):
    col_list = list(data_dict.keys())
    data_df = pd.concat(list(data_dict.values()), axis=1)
    data_df.columns = col_list
    return data_df


def prep_factor_helper(factor_name, h5_dict, pkl_dict, sdate, edate, universe=None,
                       style_data=None, fill_universe=False, operation='apppend',
                       sign_correct=True, factor_sign=None, hpr=None, return_data=False):
    """return_fac"""
    # tic1 = time.time()
    print('prep factor: %s' % (factor_name))
    h5_path = h5_dict[factor_name]
    pkl_path = pkl_dict[factor_name]
    fac_raw = IO.read_data([sdate, edate], alt=h5_path)
    col_name = fac_raw.columns[0]
    if col_name != factor_name:
        print('factor_prep_helper: h5 name(%s) not matching column name(%s) ' % (factor_name, col_name))
    fac_data_std = norm_winsor(fac_raw[col_name].unstack(), universe=universe, fill_universe=fill_universe)
    if style_data is not None:
        fac_data_neu, _, _, _ = regression_ols(fac_data_std, style_data)
        fac_data_std = norm_winsor(fac_data_neu, universe=universe, fill_universe=fill_universe)
    ic_ts = fac_data_std.corrwith(hpr, axis=1)
    if operation == 'create':
        ic_mean = ic_ts.mean()
        if ic_mean < 0 and sign_correct:
            fac_data_std = -1 * fac_data_std
    elif operation == 'append':
        if sign_correct:
            if factor_name in factor_sign:
                if factor_sign[factor_name] == -1:
                    fac_data_std = fac_data_std * -1
            else:
                print('%s not in factor_sign' % (factor_name))
                raise Exception
    update_pickle(fac_data_std, pkl_path, operation=operation)  # ,compression='gzip')
    if return_data:
        return {'ic_ts': ic_ts, 'fac_data': fac_data_std}
    else:
        return ic_ts


def find_file_by_date_helper(fname):
    fname_date = [int(i) for i in re.findall(r"\d+", fname)]
    fname_date.sort()
    sdate_fname, edate_fname = fname_date[0], fname_date[1]
    return sdate_fname, edate_fname


def find_file_by_date(base_folder, sdate, edate):
    file_list = os.listdir(base_folder)
    try:
        file_dict = {k: find_file_by_date_helper(k) for k in file_list}
        cand_dict = {k: file_dict[k] for k in file_dict if file_dict[k][0] <= sdate and file_dict[k][1] >= edate}
        cand_list = list(cand_dict.keys())
        cand_list.sort()
        file_name = os.path.join(base_folder, cand_list[-1])  # return file with latest update date
    except:
        file_name = ''
    return file_name


def generate_date_pair(sdate_min, edate_max, day_num_block=250):
    date_list = tdt.get_trading_date_range(sdate_min, edate_max)
    date_list_int = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in date_list]
    date_list_int.sort()
    # date pair - both close
    take_idx = [i for i in range(len(date_list_int)) if i % day_num_block == 0]
    date_pair_idx = [(i, i + day_num_block - 1) for i in take_idx[:-1]]
    date_pair = [(date_list_int[k[0]], date_list_int[k[1]]) for k in date_pair_idx]
    return date_pair


def get_range_pair(date_pair, sdate, edate):
    if not isinstance(sdate, int):
        sdate, edate = int(dt.datetime.strftime(sdate, '%Y%m%d')), int(dt.datetime.strftime(edate, '%Y%m%d'))
    c_idx = [i for i in range(len(date_pair))]
    l_idx = [i for i in c_idx if sdate >= date_pair[i][0]]
    r_idx = [i for i in c_idx if edate <= date_pair[i][1]]
    try:
        use_idx = [i for i in range(l_idx[-1], r_idx[0] + 1)]
    except:
        print('not in pair: %s - %s ' % (sdate, edate))
        raise Exception
    take_pair = np.array(date_pair)[use_idx].tolist()
    return take_pair


def clean_folder(folder):
    if isinstance(folder, str):
        folder = [folder]
    for pa in folder:
        if os.path.exists(pa):
            try:
                shutil.rmtree(pa)
            except:
                print('folder remove error ')
                raise Exception
        else:
            os.makedirs(pa)
    return


def process_pred(y_pred, alpha_universe):
    dat_type = check_data_type(y_pred)
    univ_type = check_data_type(alpha_universe)
    if dat_type in ['mi', 'series']:
        y_pred = y_pred.unstack()
    if univ_type in ['mi', 'series']:
        alpha_universe = alpha_universe.unstack().fillna(value=False).astype(bool)
    y_norm = norm_winsor(y_pred, alpha_universe)
    return y_norm


####################################################################################################################
""" date handler"""


def dt_parser(date):
    date_obj = dt.datetime.strptime(str(int(date)), '%Y%m%d')
    return date_obj


def handle_all_zero_parser(handle_all_zero):
    handle_type = type(handle_all_zero)
    if (handle_type == bool and handle_all_zero) or (handle_type == float):
        handle_ind = True
        if handle_type == float:
            handle_pct = handle_all_zero
        else:
            handle_pct = 0
    else:
        handle_ind = False
        handle_pct = 0
    # print(handle_type,handle_ind,handle_pct)
    return handle_ind, handle_pct


def slice_by_hpr(date_list, holding_period, ret_shift=True, get_head=False):
    # get index position n days before or later (data count for each holding period could be different)
    # get date_list removed with last hpr and ret_shift
    # ret_shift: hold account for one day shifit in holding period ~ burn more data
    # get_head: True ~ [:idx], False ~[idx:]
    # date_stop_idx ~ index position for the unique date list (positive is get_head==True)
    date_list_unique = list(set(date_list))
    date_list_unique.sort()
    date_num = len(date_list_unique)
    if get_head:  # slicing the future: prediction is okay with not enough data for last prediction task
        date_stop_idx = holding_period - 1  # index position start from 0
        if date_stop_idx > date_num - 1:
            date_stop_idx = date_num - 1
    else:  # slicing the past: training is not okay with not enough data
        date_stop_idx = -(holding_period + 2) if ret_shift else -(holding_period + 1)
        if date_stop_idx < -1 * date_num:
            print('data not enough: %d / %d' % (-1 * date_stop_idx, date_num))
            raise Exception
    date_stop = date_list_unique[date_stop_idx]
    date_list.reverse()  # reverse the list to find the last occurence
    idx_train_e = len(date_list) - date_list.index(date_stop)
    date_list.reverse()
    return idx_train_e


def align_fitting_data(y, x, alpha_universe, sdate, edate, label_cut=0.2, fillna=False):
    # hpr = calc_hpr(stock_close,holding_period)
    # check sdate,edate for all data
    x = dict2mi(x) if isinstance(x, dict) else x
    universe_mi = alpha_universe.loc[str(sdate):str(edate)].stack()
    universe_mi = universe_mi[universe_mi]
    x = x.reindex(index=universe_mi.index)  # .dropna(how='all')
    # x = x.replace([np.inf, -np.inf], np.nan)
    # make return label
    if not isinstance(y.index, pd.MultiIndex):
        y = y.stack()
    y = y.reindex(index=x.index).dropna()
    y = pd.DataFrame(y)
    x = x.reindex(index=y.index)
    if label_cut is not None:
        # cut by top and bottom pct 
        y = score2label(y, label_cut=label_cut)
    x_test = x.loc[pd.Timestamp(str(sdate)):]
    if fillna:
        x.fillna(0, inplace=True)
        x_test.fillna(0, inplace=True)
    return y, x, x_test


"""
Data Processing
"""


def check_data_type(x):
    if isinstance(x, pd.DataFrame):
        if isinstance(x.index, pd.MultiIndex):
            data_type = 'mi'
        else:
            data_type = 'matrix'
    elif isinstance(x, dict):
        data_type = 'dict'
    elif isinstance(x, pd.Series):
        if isinstance(x.index, pd.MultiIndex):
            data_type = 'mi'
        else:
            data_type = 'series'
    return data_type


def calc_hpr(stock_close, holding_period, ret_shift=True, daily_scale=False):
    if isinstance(stock_close.index, pd.MultiIndex):
        hpr = stock_close.groupby(level=1).shift(-1 * holding_period) / stock_close - 1
        if ret_shift:
            hpr = hpr.groupby(level=1).shift(-1)
    else:
        h_type = type(holding_period)
        holding_period = [holding_period] if h_type is int else holding_period
        hpr = {h: (stock_close.shift(-1 * h) / stock_close - 1) for h in holding_period}
        if ret_shift:
            hpr = {h: hpr[h].shift(-1) for h in holding_period}
        if daily_scale:
            hpr = {h: (hpr[h] + 1) ** (1 / h) - 1 for h in holding_period}
        if h_type is int:
            hpr = hpr[holding_period[0]]
    return hpr


def check_feature_importance(feature_importance, freq=None, title=None, plot=True):
    combine_weight = feature_importance.divide(feature_importance.sum(axis=1), axis=0)
    date_num = len(combine_weight)
    if freq is None:
        if date_num >= 300:
            freq = 'q'
        elif date_num >= 50:
            freq = 'm'
        else:
            freq = 'd'
    title = 'Group by ' + freq if title is None else title + ' by ' + freq
    combine_weight_mean = combine_weight.resample(freq).mean()
    combine_weight_mean = combine_weight_mean.divide(combine_weight_mean.sum(axis=1), axis=0)
    combine_weight_mean = combine_weight_mean.dropna(how='all')
    if plot:
        combine_weight_mean.plot(figsize=[11, 3], kind='bar', stacked=True, title=title)
        plt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0.)
    # fi_year = combine_weight.resample('y').mean()
    # plot_by_year(fi_year,top_n=10)
    return combine_weight_mean


def get_quick_fi(res_model, sdate=None):
    fi_raw = res_model['feature_importance']
    if isinstance(fi_raw, dict):
        fi_res_list = []
        fi_kl = list(fi_raw.keys())
        for k in fi_kl:
            fi_res_itr = pd.concat(list(fi_raw[k].values()), axis=1).mean(axis=1)
            fi_res_itr = pd.DataFrame(fi_res_itr, columns=[k])
            fi_res_list.append(fi_res_itr)
        fi_res = pd.concat(fi_res_list, axis=1).T
    else:
        fi_res = fi_raw.replace({0: np.nan})
    if sdate is not None:
        fi_res = fi_res.loc[str(sdate):]
        fi_res = fi_res.sum(axis=0).sort_values(ascending=False)
        fi_res = fi_res / fi_res.sum()
    return fi_res


def use_spec_fold_helper(res_dict_model, fold_list):
    pred_by_fold_raw = pd.concat(list(res_dict_model['misc'].values()), axis=0).sort_index()
    pred_raw_spec_fold = pred_by_fold_raw[fold_list].mean(axis=1)
    return pred_raw_spec_fold


###########################################
# new ~ 20220606


#### 20220406 1. fit with end_of_month 2. support mi format
def predict_rolling_cs_wrapper2(y, x, roll_win, holding_period, fit_pred_func=None, fit_func=None, pred_func=None,
                                process_dat_func=None, process_list=['x'],
                                rebal_freq=1, param_freq=None, expanding_window=False,
                                input_type='mi', ret_shift=True, verbose=True,
                                parallel=False, max_process=None, x_test=None, handle_nan=False,
                                handle_all_zero=True, spec_date_dict=None, test_run=None, sdate=None,
                                feature_selection_info=None, return_model=1, multi_task=False, sort_col=True):
    """
    fit_func,pred_func,process_dat_func = None,None,None
    process_list = []
    #rebal_freq=5
    expanding_window=True
    ret_shift=True
    verbose=True
    parallel=False
    #fit_pred_func=None
    x_test=None # handles for classification - prediction stage - all sample
    track_feature_importance=False
    handle_nan=False  
    param_freq = None
    input_type='mi'
    sdate = None
    spec_date_dict = None
    test_run=None
    feature_selection_info = None
    with_roll_fin: True for fill prediction with equal weight
    if param_freq is not None: esitmate parameter, pass to next function, collect parameter each iteration 
        - require fit_pred_func 1. have param output,:  res,fi,param   2. param=None, do param search, else use param
        
    #note: 
    for classification model : set_inner(alpha_universe,x,y_top_bottom)
                               need additional full universe x_test for prediction part 
    """
    max_fail = 0
    if param_freq is not None:
        if isinstance(rebal_freq, int):
            if rebal_freq > param_freq:
                raise Exception
            if rebal_freq < param_freq:
                freq_tmp = int(np.ceil(param_freq / rebal_freq) * rebal_freq)
                if freq_tmp != rebal_freq:
                    print('change param_freq from %d to %d' % (param_freq, freq_tmp), flush=True)
                    param_freq = freq_tmp
    tic = time.time()
    time_recorder = {}
    if input_type not in ['pd', 'np', 'mi']:
        raise Exception
    # align all data 
    if input_type in ['np', 'pd']:
        if isinstance(x, pd.DataFrame):
            x = {'x': x}
        input_dict_raw = {'y': y, 'x': x}
        if not multi_task:
            input_dict = align_data(input_dict_raw)
            y, x = input_dict['y'], input_dict['x']
        date_list, stk_list = y.index.tolist(), y.columns.tolist()
        x_list = list(x.keys())
        if input_type == 'np':
            y_mat = y.values
            x_mat = np.ones([len(x_list), len(date_list), len(stk_list)])  # including intercept
            i = 0
            if input_type == 'np':
                for x_name in x_list:
                    x_mat[i, :, :] = x[x_name].values
                    i = i + 1
            y, x = y_mat, x_mat
    elif input_type == 'mi':
        if sdate is not None:
            print('slice data from %d' % (sdate), flush=True)
            sdate_dt = pd.Timestamp(str(sdate))
            y = y.loc[sdate_dt:]
            x = x.loc[sdate_dt:]
        if x_test is not None:  # for classifcation need full x data - y is label already
            x = x.reindex(index=y.index).dropna()
            y = y.reindex(index=x.index).dropna()
            if sdate is not None:
                x_test = x_test.loc[sdate_dt:]
        if x.shape[0] != y.shape[0]:
            y = y.reindex(index=x.index).dropna()
        if isinstance(y.index, pd.MultiIndex):
            x_benchmark = x if x_test is None else x_test  # fix
            date_list = list(x_benchmark.index.get_level_values(level=0).unique())
            stk_list = list(x_benchmark.index.get_level_values(level=1).unique())
        else:
            if isinstance(y, pd.Series):
                y = pd.DataFrame(y)
            date_list = list(y.index.tolist())
            stk_list = list(y.columns.tolist())
    stk_num = len(stk_list)
    date_num = len(date_list)  # refer to unique date
    # add_sorting ~ 20230307 
    if sort_col:
        fac_list = x.columns.tolist()
        fac_list.sort()
        x = x[fac_list]
    if date_num < roll_win:
        print('data not enough: date_num < roll_win %d/%d' % (date_num, roll_win), flush=True)
        raise Exception
    iter_num = date_num - roll_win - holding_period
    rebal_freq_show = rebal_freq if isinstance(rebal_freq, int) else 'spec'
    print('%s | %s | %s' % ('*' * 20, 'predict_rolling_cs_wrapper', '*' * 20), flush=True)
    print('1. date num: %d, stk_num: %d' % (date_num, stk_num), flush=True)
    print('2. input_type: %s' % (input_type), flush=True)
    print('3. fit_pred_func: %s ' % (fit_pred_func), flush=True)
    print('4. rebal_freq: %s, param_freq: %s, test_run: %s ' % (str(rebal_freq_show), str(param_freq), str(test_run)), flush=True)
    print('5. roll_win: %s, holding_period: %s, expanding_window: %s' % (str(roll_win), str(holding_period), str(expanding_window)), flush=True)
    holding_period = max(holding_period, 1)
    start_idx = roll_win + holding_period + 1 if ret_shift else roll_win + holding_period  # refer to unique
    # get idx by rebal_freq slice or spec_rebal_list
    if isinstance(rebal_freq, int):
        idx_list_rebal = [i for i in range(start_idx, date_num) if (i - start_idx) % rebal_freq == 0]  # refer to unique
    else:
        idx_list_rebal = [i for i in range(start_idx, date_num) if date_list[i] in rebal_freq]
    if isinstance(x.index, pd.MultiIndex):  # handles mutlindex date ~ universal model
        date_list_full = x.index.get_level_values(level=0).to_list()
        date_list_unique = list(set(date_list_full))
        date_list_unique.sort()
        date_num_full = len(date_list_full)
        date_num_unique = len(date_list_unique)
        if date_num_full > date_num_unique:
            date_list_rebal = [date_list_unique[i] for i in idx_list_rebal]
            date_list_full.reverse()  # reverse to find the last occurence
            idx_list_rebal_rev = [date_list_full.index(i) for i in date_list_rebal]
            # refer to full ~ idx as end of occurence for the current timestamp
            idx_list_rebal = [date_num_full - i - 1 for i in idx_list_rebal_rev]
            idx_list_rebal = [i for i in idx_list_rebal if i < date_num_full]
            print('    pred with multiindex: %d days with %d rows' % (len(date_list_unique), len(date_list_full)), flush=True)
            date_list_full.reverse()  # reverse back
            date_list = date_list_full  # refer to full
    if spec_date_dict is not None:
        spec_list = list(spec_date_dict.keys())
        spec_list = [i for i in spec_list if i in date_list]
        idx_list_spec = [date_list.index(i) for i in spec_list]
        orig_num = len(idx_list_rebal)
        idx_list_rebal = list(np.intersect1d(idx_list_rebal, idx_list_spec))
        new_num = len(idx_list_rebal)
        print('slice by spec_date_list: %d/%d' % (new_num, orig_num), flush=True)
    if param_freq is not None:
        idx_list_param = [i for i in range(start_idx, date_num) if (i - start_idx) % param_freq == 0]
    date_list_int = [dt.datetime.strftime(i, '%Y%m%d') for i in date_list]
    if test_run is not None:  # if test_run<0 use only last n iteration
        if isinstance(test_run, int):
            if test_run < 0:
                print('test run for %s iteration' % (str(test_run)), flush=True)
                idx_list_rebal_use = idx_list_rebal[test_run:]
            elif test_run > 0:
                print('test run for %s sampling' % (str(test_run)), flush=True)
                run_num = len(idx_list_rebal)
                div_num = int(np.floor(run_num / test_run))
                div_list = [idx_list_rebal[i] for i in range(run_num) if i % div_num == 0]
                if len(div_list) > test_run:
                    div_list = div_list[-test_run:]
                idx_list_rebal_use = div_list
    else:
        idx_list_rebal_use = idx_list_rebal  # refer to full
    pred_num = len(idx_list_rebal_use)
    print('6. iteration number: %d ' % (pred_num), flush=True)
    # assgin iter model
    pred_cs_iter = partial(predict_rolling_cs_iter2,
                           date_list=date_list, fit_func=fit_func, pred_func=pred_func,
                           y=y, x=x, roll_win=roll_win, holding_period=holding_period,
                           process_dat_func=process_dat_func, process_list=process_list,
                           rebal_freq=rebal_freq, param_freq=param_freq,
                           expanding_window=expanding_window, input_type=input_type,
                           fit_pred_func=fit_pred_func, x_test=x_test,
                           handle_nan=handle_nan, handle_all_zero=handle_all_zero,
                           spec_date_dict=spec_date_dict,
                           feature_selection_info=feature_selection_info, verbose=verbose)
    # collect list
    res_list, score_list = [], []  # dataframe format
    fi_dict, param_dict, misc_dict, misc_dict, model_dict = {}, {}, {}, {}, {}  # dictionary format
    collect_list = ['prediction', 'feature_importance', 'misc', 'model', 'score', 'parameter']
    if parallel:
        if param_freq is not None:
            print('parallel not support for parameter re-estimate!', flush=True)
            raise Exception
        res_dict = multiprocess_wrapper(func=pred_cs_iter, iter_list=idx_list_rebal_use, collect_output=True,
                                        max_process=max_process)
        idx_list = list(res_dict.keys())
        idx_date_list = [date_list[i] for i in idx_list]
        res_dict = {date_list[i]: res_dict[i] for i in res_dict}  # replace key
        key_list = list(res_dict[idx_date_list[0]].keys())
        for i in res_dict:
            res_list.append(res_dict[i]['prediction'])
        if 'feature_importance' in key_list:
            fi_dict = {i: res_dict[i]['feature_importance'] for i in res_dict}
        if 'score' in key_list:
            score_list.append(res_dict[i]['score'])
        if 'parameter' in key_list:
            param_dict = {i: res_dict[i]['parameter'] for i in res_dict}
        if 'misc' in key_list:
            misc_dict = {i: res_dict[i]['misc'] for i in res_dict}
        if 'model' in key_list:
            model_dict = {i: res_dict[i]['model'] for i in res_dict}
    else:
        iter_idx, fail_cnt = 0, 0  # by iteration training & collect
        for idx in idx_list_rebal_use:
            try:
                tic_iter = time.time()
                iter_idx = iter_idx + 1
                if verbose:
                    print('%d/%d start: %s' % (iter_idx, pred_num, date_list_int[idx]), flush=True)
                if param_freq is not None:  # re-estimate parameter
                    if idx in idx_list_param:  # idx: end date for training, idx+1 for prediction
                        print('%d/%d - train for optimal parameter' % (iter_idx, pred_num), flush=True)
                        pred_cs_iter = partial(pred_cs_iter, fit_pred_func=fit_pred_func)  # re-assign
                        res_iter_dict = pred_cs_iter(idx)
                        # re-estimate params / collect param / assign new function
                        fit_pred_func_opt = partial(fit_pred_func, param=res_iter_dict['parameter'])
                        pred_cs_iter = partial(pred_cs_iter, fit_pred_func=fit_pred_func_opt)
                        param_str = '(param search iter)'
                    else:
                        res_iter_dict = pred_cs_iter(idx)
                        param_str = ''
                else:
                    res_iter_dict = pred_cs_iter(idx)
                    param_str = ''
                time_iter = date_list[idx]
                if 'prediction' in res_iter_dict:
                    res_list.append(res_iter_dict['prediction'])
                if 'feature_importance' in res_iter_dict:
                    fi_dict[time_iter] = res_iter_dict['feature_importance']
                if 'parameter' in res_iter_dict:
                    param_dict[time_iter] = res_iter_dict['parameter']
                if 'misc' in res_iter_dict:
                    misc_dict[time_iter] = res_iter_dict['misc']
                if 'model' in res_iter_dict:
                    # if isinstance(return_model,int):
                    return_model = abs(return_model)
                    last_count = len(idx_list_rebal_use) - idx_list_rebal_use.index(idx)
                    if last_count <= return_model:
                        print('save last model %d' % (last_count), flush=True)
                        model_dict[time_iter] = res_iter_dict['model']
                    else:
                        model_dict[time_iter] = None
                if 'score' in res_iter_dict:
                    score_list.append(res_iter_dict['score'])

                toc_iter = time.time()
                remain_iter = pred_num - iter_idx
                time_iter = print_time(toc_iter, tic_iter, show_time=True, remain_iter=remain_iter)
                time_recorder[iter_idx] = time_iter
                if verbose:
                    print('%d/%d done %s- %s - %s' % (iter_idx, pred_num, param_str, date_list_int[idx], time_iter), flush=True)
                    print('*' * 20, flush=True)
            except Exception as e:
                print('%s' % (e), flush=True)
                fail_cnt = fail_cnt + 1
                print('%d/%d - %s - failed' % (iter_idx, iter_num, date_list[idx]), flush=True)
                if fail_cnt > max_fail:
                    print('failed over %d times' % (fail_cnt), flush=True)
                    raise Exception
    print('predict raw finished', flush=True)
    print('collect prediction result', flush=True)
    res_dict = {}
    if len(res_list) > 0:  # collect prediction result
        if isinstance(res_list[0], pd.DataFrame) or isinstance(res_list[0], pd.Series):
            res = pd.concat(res_list, axis=0)
            if isinstance(res.index, pd.MultiIndex):
                try:
                    res = res.unstack()
                except:
                    print(res_list[-2][-1], res_list[-1][0], flush=True)
        elif isinstance(res_list[0], dict):
            if 'prediction' in res_list[0]:
                res_list = [i['prediction'] for i in res_list]
                res = pd.concat(res_list, axis=0)
        res = res.sort_index()
        res_dict['prediction'] = res
    else:
        print('prediction failed with no values', flush=True)
        raise Exception
    # collect feature importance 
    if len(list(fi_dict.keys())) > 0:
        print('collect feature importance', flush=True)
        res_dict['feature_importance'] = fi_dict
    # collect score
    if len(score_list) > 0:
        print('collect score', flush=True)
        if isinstance(score_list[0], pd.DataFrame) or isinstance(score_list[0], pd.Series):
            score = pd.concat(score_list, axis=1).T
            if isinstance(score.index, pd.MultiIndex):
                score_pd = score.unstack()
        elif isinstance(score_list[0], dict):
            if 'prediction' in score_list[0]:
                score_list = [i['score'] for i in score_list]
                score_list = pd.concat(score_list, axis=1).T
    toc = time.time()
    print('%s | predict done | %s - %s' % ('*' * 20, '*' * 20, print_time(toc, tic)), flush=True)
    if param_freq is not None:
        res_dict['parameter'] = param_dict
    res_dict['misc'] = misc_dict
    res_dict['model'] = model_dict
    res_dict['score'] = score_list
    res_dict['time'] = time_recorder
    print(time_recorder, flush=True)
    return res_dict


# 20210611 - fix for ts_mi
# 20220403 - fix for month_end_friday training

def predict_rolling_cs_iter2(idx, date_list, fit_func, pred_func, y, x, roll_win, holding_period,
                             process_dat_func=None, process_list=['x'],
                             rebal_freq=1, param_freq=None, expanding_window=False,
                             input_type='pd', ret_shift=True, fit_pred_func=None, x_test=None,
                             handle_nan=False, handle_all_zero=True, spec_date_dict=None,
                             feature_selection_info=None, verbose=False):
    # holding period return mark at the start 
    # idx current end position for training,idx+1 for prediction
    collect_list = ['prediction', 'feature_importance', 'parameter', 'misc', 'score', 'model']
    date_num_full = len(date_list)
    if isinstance(y, pd.Series):
        y = pd.DataFrame(y)
        # get idx_train_s,idx_train_e,idx_test_s,idx_test_e
    idx_train_e = slice_by_hpr2(date_list[:idx], day_num=holding_period,
                                direction='backward',
                                check_point='end',
                                ret_shift=True) + 1
    if expanding_window:
        idx_train_s = 0
        window_type = 'expanding'
    else:
        idx_train_s = slice_by_hpr2(date_list[:idx], day_num=holding_period + roll_win,
                                    direction='backward',
                                    check_point='start',
                                    ret_shift=True)
        window_type = 'fixed'
    if idx >= date_num_full - 1:
        # print('%d / %d'%(idx,date_num_full-1))
        print('no need for prediction for this iteration: %s' % (str(y.iloc[idx].name)), flush=True)
        pred_ind = False
    else:
        pred_ind = True
    if pred_ind:
        idx_test_s = idx + 1
        if isinstance(rebal_freq, int):
            pred_len = rebal_freq
        else:
            idx_rebal_curr = rebal_freq.index(date_list[idx])
            if idx_rebal_curr < len(rebal_freq) - 1:
                rebal_date_next = rebal_freq[idx_rebal_curr + 1]
                idx_next = find_last_helper2(rebal_date_next, date_list)
            else:
                idx_next = len(date_list)
            pred_len = len(set(date_list[idx + 1:idx_next + 1]))  # should be 2
        idx_test_e = idx + slice_by_hpr2(date_list[idx + 1:], day_num=pred_len, direction='forward',
                                         check_point='end', ret_shift=False) + 1
        idx_test_e = min(idx_test_e, date_num_full - 1)
    else:  # must nullify prediction result in the end
        idx_test_s = idx - 1
        idx_test_e = idx

    # to account of idx could be last point of training & no data for prediction 

    x_train_iter, y_train_iter, x_test_iter = None, None, None
    if input_type == 'np':
        x_test_iter = x[:, idx_test_s:idx_test_e, :]
        if fit_func is not None:
            y_train_iter = y[idx_train_s:idx_train_e, :]
            x_train_iter = x[:, idx_train_s:idx_train_e, :]
    elif input_type == 'pd':
        x_test_iter = {k: x[k].iloc[idx_test_s:idx_test_e + 1] for k in x}
        if fit_func is not None:
            y_train_iter = y.iloc[idx_train_s:idx_train_e]
            x_train_iter = {k: x[k].iloc[idx_train_s:idx_train_e] for k in x}
    elif input_type == 'mi':
        x_test_iter = x.iloc[idx_test_s:idx_test_e + 1, :]
        if x_test is not None:  # use full x_test data ~ assume index coverage is full
            date_list_test = x_test.index.tolist()
            sdate_test_dt, edate_test_dt = x_test_iter.index[0], x_test_iter.index[-1]
            sdate_test_idx = date_list_test.index(sdate_test_dt)
            date_list_test.reverse()
            edate_test_idx = len(date_list_test) - date_list_test.index(edate_test_dt)
            x_test_iter = x_test.iloc[sdate_test_idx:edate_test_idx, :]
        if fit_func is not None or fit_pred_func is not None:
            if spec_date_dict is None:
                date_list_train_iter = date_list[idx_train_s:idx_train_e]
            else:
                date_list_train_iter = spec_date_dict[date_list[idx]]
            y_train_iter = y.iloc[idx_train_s:idx_train_e]
            x_train_iter = x.iloc[idx_train_s:idx_train_e]
    if handle_nan:
        if x_train_iter is not None:
            col_mask_x = np.isfinite(x_test_iter + np.sum(x_train_iter, axis=0))
        else:
            col_mask_x = np.isfinite(x_test_iter)
        col_num = np.count_nonzero(col_mask_x)
        if col_num == 0:
            print('Warning: X variable empty', flush=True)
            raise Exception
        elif col_num > 0 and col_num < x.shape[1]:  # asssume data continuous in train, in test
            col_use = col_mask_x[col_mask_x].columns
            x_test_iter = x_test_iter[col_use]
            x_train_iter = x_train_iter[col_use]
        print('handle_nan: %s ~ %d' % (x_train_iter.shape[1], len(col_use)), flush=True)
    handle_ind, handle_pct = handle_all_zero_parser(handle_all_zero)
    if handle_ind:
        x_len = x_train_iter.shape[0]
        nonzero_count = (x_train_iter != 0).sum(axis=0)
        nonzero_pct = nonzero_count / x_len
        zero_list = nonzero_pct[nonzero_pct <= handle_pct].index.tolist()
        if len(zero_list) > 0:
            all_list = x_train_iter.columns.tolist()
            take_list = [i for i in all_list if i not in zero_list]
            print('remove all zero list ~ remain: %d/%d' % (len(take_list), len(all_list)), flush=True)
            x_train_iter = x_train_iter[take_list]
            x_test_iter = x_test_iter[take_list]
    print('handle_ind: %s' % (str(x_train_iter.shape)), flush=True)
    # prep 
    if process_dat_func is not None:
        if process_list == 'x':
            # x_train_iter,x_test_iter = process_dat_func(x_train_iter,x_test_iter)
            scaler_dict = process_dat_func(x_train_iter, x_test_iter)
            x_train_iter, x_test_iter = scaler_dict['train'], scaler_dict['test']
        elif process_list == 'y':
            # y_train_iter = process_dat_func(y_train_iter)
            scaler_dict_y = process_dat_func(y_train_iter)
            y_train_iter = scaler_dict_y['train']
        elif process_list == 'xy':
            scaler_dict = process_dat_func(x_train_iter, x_test_iter)
            scaler_dict_y = process_dat_func(y_train_iter)
            y_train_iter = scaler_dict_y['train']
            x_train_iter, x_test_iter = scaler_dict['train'], scaler_dict['test']
            print('process_dat_func: %s' % (str(x_train_iter.shape)), flush=True)
    if feature_selection_info is not None:
        edate_train_iter = x_train_iter.iloc[-1:].index
        if isinstance(edate_train_iter, pd.MultiIndex):
            edate_train_iter = edate_train_iter[0]
        fs_itr = feature_selection_info.loc[edate_train_iter]
        if isinstance(fs_itr.index, pd.MultiIndex):
            fs_itr_slice = fs_itr.sum()
        else:
            fs_itr_slice = fs_itr
        fac_list_iter = fs_itr_slice[fs_itr_slice > 0].index.tolist()
        x_list_iter = x_train_iter.columns.tolist()
        x_list_iter2 = x_test_iter.columns.tolist()
        use_list_iter = list(set(x_list_iter).intersection(set(fac_list_iter)).intersection(set(x_list_iter2)))
        if len(use_list_iter) == 0:
            print('use_list_iter is empty: %s' % (str(use_list_iter)), flush=True)
            raise Exception
        x_train_iter = x_train_iter[use_list_iter]
        x_test_iter = x_test_iter[use_list_iter]
    # fit & pred 
    if verbose:
        print('%s window: used %d days ~ %d rows | feature %d/%d' % (window_type, roll_win, len(x_train_iter), x_train_iter.shape[1], x.shape[1]), flush=True)
        print('train set: %d %s ~ %s' % (idx_train_e - idx_train_s + 1, str(x_train_iter.index[0]), str(x_train_iter.index[-1])), flush=True)
        print('test set: %d %s ~ %s' % (idx_test_e - idx_test_s + 1, str(x_test_iter.index[0]), str(x_test_iter.index[-1])), flush=True)

    if fit_pred_func is None:
        if fit_func is not None:
            try:
                model_iter = fit_func(y_train_iter, x_train_iter)
            except:
                print('fit error -%s' % (fit_func), flush=True)
                raise Exception
            pred_tmp = pred_func(x_test_iter, model_iter)
        else:
            pred_tmp = pred_func(x_test_iter)
    else:
        res_contain = fit_pred_func(y_train_iter, x_train_iter, x_test_iter)
        res_iter_dict = {}
        if isinstance(res_contain, dict):
            for collect_name in collect_list:
                if collect_name in res_contain:
                    res_tmp = res_contain[collect_name]
                    if collect_name == 'prediction' and isinstance(res_tmp, np.ndarray):
                        res_tmp = pd.DataFrame(res_tmp, index=x_test_iter.index)
                    res_iter_dict[collect_name] = res_tmp
        else:
            print('output format error for res_contain', flush=True)
            raise Exception
    if not pred_ind:
        print('last model training ~ needs no prediction', flush=True)
        res_iter_dict['prediction'] = None
    return res_iter_dict


def find_last_helper2(val, list_use):
    list_rev = copy.deepcopy(list_use)
    list_rev.reverse()
    last_idx = len(list_use) - list_rev.index(val) - 1
    return last_idx


def slice_by_hpr2(date_list, day_num, direction='backward', check_point='start', ret_shift=True):
    # idx_train_s: backward ~ start
    # idx_train_e: backward ~ end 
    # idx_test_s: forward ~ start
    # idx_test_e: forward ~ end ~ handle for not enough data for prediction
    date_list_unique = list(set(date_list))
    date_list_unique.sort()
    date_num_unique = len(date_list_unique)
    day_gap = day_num + 2 if ret_shift else day_num + 1
    if direction == 'backward':
        date_use = date_list_unique[-1 * day_gap]
    elif direction == 'forward':
        if len(date_list_unique) > day_gap:
            date_use = date_list_unique[day_gap - 2]
        else:
            date_use = date_list_unique[-1]
    if check_point == 'start':
        idx_use = date_list.index(date_use)
    elif check_point == 'end':
        idx_use = find_last_helper2(date_use, date_list)
    return idx_use

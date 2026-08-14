import sys
sys.path.append('/data/user/015836/HANXU/alphaResearch/dataUpdate/')


from TSmodel.RealTime.FixFactorTest import get_stock_pool, get_future, get_nolimit, get_std_factor

from dataApi.stockList import trans_windcode2int
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date, get_date_range, \
    get_desample_minute_dict, trade_minutes

from multiprocessing import Pool
from functools import reduce
import pandas as pd
import numpy as np
import time
import gc
import re
import os

def multiprocess(lines, func, iterable, *args):
    pool = Pool(processes=lines)
    print('多进程启动')
    pool_apply_async = {}
    for j in range(lines):
        sub_iter = iterable[j::lines]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args + (j,))
    pool.close()
    print('等待%s个进程全部完成...' % lines)
    pool.join()
    print('多进程结束！')
    return pool_apply_async

def get_fix_factor_list(restore=False, factor_address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/'):

    if restore:
        factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
        freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
        factor_list = sorted(list({x[8:-4] for x in os.listdir(
            factor_address) if re.match('^Fix1[0134][03]0_', x)}))
        factor_list = [x for x in factor_list if len([y for y in os.listdir(
            factor_address) if x in y and len(x) == len(y) - 12]) == len(freq)]
    else:
        remove_list = ['idx_date', 'idx_time', 'idx_code', 'nolimit', 'future', 'raw_idx_date', 'raw_idx_code']
        factor_list = sorted([x[:-4] for x in os.listdir(factor_address) if (x[:-4] not in remove_list) & (x[0] != '_')])
    return factor_list

def _load_pickle_frame(file_name, date_list, code_list=None):

    factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
    freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    df_dic = {}
    for time in freq:
        df = pd.read_pickle(factor_address + 'Fix%s_' % time + file_name + '.pkl')
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.reindex(date_list, code_list)
        df = df.loc[:df.dropna(how='all').index[-1]]
        df_dic[time] = df
    axis0 = reduce(min, [df_dic[x].shape[0] for x in df_dic])
    return np.r_['0,3', tuple(df_dic[x].values[:axis0] for x in freq)].transpose(1, 0, 2)

def _create_factor_head(file_name, address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/'):

    head = [38889, 26093, 32, 20013, 22269, 20154, 27665, 22823, 23398, 32, 27721, 38738,
            39640, 32423, 32463, 27982, 19982, 37329, 34701, 30740, 31350, 38498, 32,
            37327, 21270, 37329, 34701, 32, 50, 48, 49, 55]
    head = np.array(head, dtype='int32')
    head.tofile('%s/%s.npy' % (address, file_name))

def _get_file_size(file_name, address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/'):

    size = os.path.getsize('%s/%s.npy' % (address, file_name))
    return size

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

def init_update(address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
                restore_start_date=0, end_date=None, fix_freq=7):

    if restore_start_date:
        end_date = min(get_recent_trade_date(end_date), get_pre_trade_date(dividing_point=18))
        date_list = get_date_range(restore_start_date, end_date)
        test_date_list = get_date_range(get_pre_trade_date(date_list[0]), end_date)

        period = 1 if fix_freq == 242 else (30 if fix_freq == 7 else 240 // fix_freq)
        period_list = sorted(list(set(get_desample_minute_dict(
            period).values()))) if period > 1 else trade_minutes
        period_list = period_list[:-1] if fix_freq == 7 else period_list

        stock_pool = get_stock_pool(test_date_list)
        code_list = stock_pool.columns.to_list()
        stock_pool = stock_pool.values

        idx_date = (np.array(test_date_list)[1:, None] + np.zeros((len(code_list)), dtype=int))[
            stock_pool[1:]].astype(np.int32)
        idx_code = (np.array(code_list)[None, :] + np.zeros((len(test_date_list) - 1, 1), dtype=int))[
            stock_pool[1:]].astype(np.int32)
        idx_time = np.array(period_list[1:] + period_list).astype(np.int16)

        np.save('%s/idx_date.npy' % address, idx_date)
        np.save('%s/idx_code.npy' % address, idx_code)
        np.save('%s/idx_time.npy' % address, idx_time)

        future = get_future(test_date_list, code_list)
        nolimit = get_nolimit(test_date_list, code_list)

        future = future[1:][stock_pool[1:]].astype(np.float32)
        nolimit = nolimit[1:][stock_pool[1:]]

        _create_factor_head('future', address)
        offset = _get_file_size('future', address)
        fp = np.memmap('%s/future.npy' % address, dtype='float32', mode='r+', shape=future.shape, offset=offset)
        fp[:] = future
        del fp

        _create_factor_head('nolimit', address)
        offset = _get_file_size('nolimit', address)
        fp = np.memmap('%s/nolimit.npy' % address, dtype='bool', mode='r+', shape=nolimit.shape, offset=offset)
        fp[:] = nolimit
        del fp

    else:
        if not os.path.exists('%s/idx_date.npy' % address):
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  "No original file found, restore init files from 20140801 instead.")
            init_update(address, 20140801, end_date, fix_freq)
            return None

        end_date = get_recent_trade_date(end_date, dividing_point=18)
        idx_date = np.load('%s/idx_date.npy' % address)
        idx_code = np.load('%s/idx_code.npy' % address)
        update_start_date = idx_date[-1]
        if update_start_date >= end_date:
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  f"idx_date has already been updated to {update_start_date}, no need to update to {end_date}.")
        else:
            test_date_list = get_date_range(update_start_date, end_date)
            stock_pool = get_stock_pool(test_date_list)
            code_list = stock_pool.columns.to_list()
            stock_pool = stock_pool.values
            _idx_date = (np.array(test_date_list)[1:, None] + np.zeros((len(code_list)), dtype=int))[
                stock_pool[1:]].astype(np.int32)
            _idx_code = (np.array(code_list)[None, :] + np.zeros((len(test_date_list) - 1, 1), dtype=int))[
                stock_pool[1:]].astype(np.int32)
            idx_date = np.r_[idx_date, _idx_date].astype(np.int32)
            idx_code = np.r_[idx_code, _idx_code].astype(np.int32)
            np.save('%s/idx_date.npy' % address, idx_date)
            np.save('%s/idx_code.npy' % address, idx_code)
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  f"idx_date is updated from {update_start_date} to {end_date} successfully.")

        future_size = _get_file_size('future', address)
        future_end_date_idx = (future_size - 128) // (4 * fix_freq)
        if future_end_date_idx >= idx_date.shape[0]:
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  f"future has already been updated to {end_date}, no need to update to {end_date}.")
        elif idx_date[future_end_date_idx] > min(end_date, get_pre_trade_date(dividing_point=18)):
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  f"future has already been updated to {end_date}, no need to update to {end_date}.")
        else:
            idx_choose = idx_date[future_end_date_idx:] <= min(end_date, get_pre_trade_date(dividing_point=18))
            update_date = idx_date[future_end_date_idx:][idx_choose]
            update_code = idx_code[future_end_date_idx:][idx_choose]
            stock_pool, date_list, code_list = infer_stock_pool(update_date, update_code)
            try:
                future = get_future(date_list, code_list)
            except ValueError:
                print(time.strftime('%Y%m%d %H:%M:%S'), "future data has not arrived.")
            else:
                future = future[stock_pool].astype(np.float32)
                fp = np.memmap('%s/future.npy' % address, dtype='float32', mode='r+', shape=future.shape,
                               offset=future_size)
                fp[:] = future
                del fp
                print(time.strftime('%Y%m%d %H:%M:%S'),
                      f"future is updated from {date_list[0]} to {date_list[-1]} successfully.")

        nolimit_size = _get_file_size('nolimit', address)
        nolimit_end_date_idx = (nolimit_size - 128) // fix_freq
        if nolimit_end_date_idx >= idx_date.shape[0]:
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  f"nolimit has already been updated to {end_date}, no need to update to {end_date}.")
        elif idx_date[nolimit_end_date_idx] > min(end_date, get_pre_trade_date(dividing_point=18)):
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  f"future has already been updated to {end_date}, no need to update to {end_date}.")
        else:
            idx_choose = idx_date[nolimit_end_date_idx:] <= min(end_date, get_pre_trade_date(dividing_point=18))
            update_date = idx_date[nolimit_end_date_idx:][idx_choose]
            update_code = idx_code[nolimit_end_date_idx:][idx_choose]
            stock_pool, date_list, code_list = infer_stock_pool(update_date, update_code)
            try:
                nolimit = get_nolimit(date_list, code_list)
            except ValueError:
                print(time.strftime('%Y%m%d %H:%M:%S'), "nolimit data has not arrived.")
            else:
                nolimit = nolimit[stock_pool]
                fp = np.memmap('%s/nolimit.npy' % address, dtype='bool', mode='r+', shape=nolimit.shape,
                               offset=nolimit_size)
                fp[:] = nolimit
                del fp
                print(time.strftime('%Y%m%d %H:%M:%S'),
                      f"nolimit is updated from {date_list[0]} to {date_list[-1]} successfully.")

def init_amend(address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/',
               amend_start_date=20210813, end_date=None, fix_freq=7):

    if not os.path.exists('%s/idx_date.npy' % address):
        print(time.strftime('%Y%m%d %H:%M:%S'),
              "No original file found, restore init files from 20140801 instead.")
        init_update(address, 20140801, end_date, fix_freq)
        return None

    if not amend_start_date:
        amend_start_date = get_pre_trade_date(np.load('%s/idx_date.npy' % address)[-1], -1)
    end_date = get_recent_trade_date(end_date, dividing_point=18)
    amend_date_list = get_date_range(amend_start_date, end_date)
    amend_start_date = amend_date_list[0]
    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    idx_code = idx_code[idx_date < amend_start_date]
    idx_date = idx_date[idx_date < amend_start_date]
    before_len = idx_date.shape[0]

    stock_pool = get_stock_pool(amend_date_list)
    code_list = stock_pool.columns.to_list()
    stock_pool = stock_pool.values
    _idx_date = (np.array(amend_date_list)[:, None] + np.zeros((len(code_list)), dtype=int))[
        stock_pool].astype(np.int32)
    _idx_code = (np.array(code_list)[None, :] + np.zeros((len(amend_date_list), 1), dtype=int))[
        stock_pool].astype(np.int32)
    idx_date = np.r_[idx_date, _idx_date].astype(np.int32)
    idx_code = np.r_[idx_code, _idx_code].astype(np.int32)
    np.save('%s/idx_date.npy' % address, idx_date)
    np.save('%s/idx_code.npy' % address, idx_code)
    print(time.strftime('%Y%m%d %H:%M:%S'),
          f"idx_date is amended from {amend_start_date} to {end_date} successfully.")

    future_size = before_len * 4 * fix_freq + 128
    idx_choose = idx_date[before_len:] <= end_date
    update_date = idx_date[before_len:][idx_choose]
    update_code = idx_code[before_len:][idx_choose]
    stock_pool, date_list, code_list = infer_stock_pool(update_date, update_code)
    try:
        future = get_future(date_list, code_list)
    except ValueError:
        print(time.strftime('%Y%m%d %H:%M:%S'), "future data has not arrived.")
    else:
        future = future[stock_pool].astype(np.float32)
        fp = np.memmap('%s/future.npy' % address, dtype='float32', mode='r+', shape=future.shape,
                       offset=future_size)
        fp[:] = future
        del fp
        print(time.strftime('%Y%m%d %H:%M:%S'),
              f"future is amended from {amend_start_date} to {end_date} successfully.")

    nolimit_size = before_len * fix_freq + 128
    idx_choose = idx_date[before_len:] <= end_date
    update_date = idx_date[before_len:][idx_choose]
    update_code = idx_code[before_len:][idx_choose]
    stock_pool, date_list, code_list = infer_stock_pool(update_date, update_code)
    try:
        nolimit = get_nolimit(date_list, code_list)
    except ValueError:
        print(time.strftime('%Y%m%d %H:%M:%S'), "nolimit data has not arrived.")
    else:
        nolimit = nolimit[stock_pool]
        fp = np.memmap('%s/nolimit.npy' % address, dtype='bool', mode='r+', shape=nolimit.shape,
                       offset=nolimit_size)
        fp[:] = nolimit
        del fp
        print(time.strftime('%Y%m%d %H:%M:%S'),
              f"nolimit is amended from {amend_start_date} to {end_date} successfully.")

def store_factor(factor_name, restore_start_date=0, end_date=None, standardize_days=40, freq=7,
                 address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/'):

    idx_date = np.load('%s/data/idx_date.npy' % address)
    idx_code = np.load('%s/data/idx_code.npy' % address)
    end_date = get_recent_trade_date(end_date, dividing_point=18)

    if restore_start_date:
        date_list = get_date_range(restore_start_date, end_date)
        start_date = date_list[0]
        if start_date != idx_date[0]:
            raise ValueError("restore_start_date must be consist with the start of idx_date.")
        select_idx = idx_date <= end_date
        store_date = idx_date[select_idx]
        store_code = idx_code[select_idx]
        stock_pool, date_list, code_list = infer_stock_pool(store_date, store_code)
        calc_start_date = get_pre_trade_date(start_date, standardize_days + 1)
        calc_date_list = get_date_range(calc_start_date, end_date)

        factor = _load_pickle_frame(factor_name, calc_date_list, code_list)
        if factor.shape[0] < len(calc_date_list):
            print(time.strftime('%Y%m%d %H:%M:%S'), f"factor {factor_name} data has not arrived.")
            if factor.shape[0] <= standardize_days + 1:
                return
            else:
                miss_days = len(calc_date_list) - factor.shape[0]
                stock_pool = stock_pool[:-miss_days]
        factor, mean, std = get_std_factor(factor, standardize_days, freq, standardize_days)
        mean = mean[1:][stock_pool].astype(np.float64)
        std = std[1:][stock_pool].astype(np.float64)
        factor = np.concatenate((factor[:-1, 1:], factor[1:]), axis=1).transpose(0, 2, 1)[stock_pool].astype(np.float32)

        _create_factor_head(factor_name, f'{address}/data/')
        offset = _get_file_size(factor_name, f'{address}/data/')
        fp = np.memmap('%s/data/%s.npy' % (address, factor_name),
                       dtype='float32', mode='r+', shape=factor.shape, offset=offset)
        fp[:] = factor
        del fp
        gc.collect()

        _create_factor_head(factor_name, f'{address}/mean/')
        offset = _get_file_size(factor_name, f'{address}/mean/')
        fp = np.memmap('%s/mean/%s.npy' % (address, factor_name),
                       dtype='float64', mode='r+', shape=mean.shape, offset=offset)
        fp[:] = mean
        del fp
        gc.collect()

        _create_factor_head(factor_name, f'{address}/std/')
        offset = _get_file_size(factor_name, f'{address}/std/')
        fp = np.memmap('%s/std/%s.npy' % (address, factor_name),
                       dtype='float64', mode='r+', shape=std.shape, offset=offset)
        fp[:] = std
        del fp
        gc.collect()

    else:
        if not os.path.exists(f'{address}/data/{factor_name}.npy'):
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  f"factor {factor_name} not found, restore factor from 20140801 instead.")
            store_factor(factor_name, 20140801, end_date, standardize_days, freq, address)
            return None

        idx_date = np.load('%s/data/idx_date.npy' % address)
        idx_code = np.load('%s/data/idx_code.npy' % address)

        factor_size = _get_file_size(factor_name, f'{address}/data/')
        factor_end_date_idx = (factor_size - 128) // (4 * (2 * freq - 1))
        if factor_end_date_idx >= idx_date.shape[0]:
            print(time.strftime('%Y%m%d %H:%M:%S'),
                  f"factor {factor_name} has already been updated to {end_date}, no need to update to {end_date}.")
        else:
            update_start_date = idx_date[factor_end_date_idx]
            calc_start_date = get_pre_trade_date(update_start_date, standardize_days + 1)
            calc_date_list = get_date_range(calc_start_date, end_date)
            select_idx = (idx_date <= end_date) & (idx_date >= update_start_date)
            store_date = idx_date[select_idx]
            store_code = idx_code[select_idx]
            stock_pool, date_list, code_list = infer_stock_pool(store_date, store_code)

            factor = _load_pickle_frame(factor_name, calc_date_list, code_list)
            if factor.shape[0] < len(calc_date_list):
                print(time.strftime('%Y%m%d %H:%M:%S'), f"factor {factor_name} data has not arrived.")
                if factor.shape[0] <= standardize_days + 1:
                    return
                else:
                    miss_days = len(calc_date_list) - factor.shape[0]
                    stock_pool = stock_pool[:-miss_days]
            factor, mean, std = get_std_factor(factor, standardize_days, freq, standardize_days)
            mean = mean[1:][stock_pool].astype(np.float64)
            std = std[1:][stock_pool].astype(np.float64)
            factor = np.concatenate((factor[:-1, 1:], factor[1:]), axis=1).transpose(0, 2, 1)[stock_pool].astype(
                np.float32)

            fp = np.memmap('%s/data/%s.npy' % (address, factor_name),
                           dtype='float32', mode='r+', shape=factor.shape, offset=factor_size)
            fp[:] = factor
            del fp
            gc.collect()

            mean_size = factor_end_date_idx * 8 + 128
            fp = np.memmap('%s/mean/%s.npy' % (address, factor_name),
                           dtype='float64', mode='r+', shape=mean.shape, offset=mean_size)
            fp[:] = mean
            del fp
            gc.collect()

            fp = np.memmap('%s/std/%s.npy' % (address, factor_name),
                           dtype='float64', mode='r+', shape=std.shape, offset=mean_size)
            fp[:] = std
            del fp
            gc.collect()

def amend_factor(factor_name, amend_start_date=20210813, end_date=None, standardize_days=40, freq=7,
                 address='/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/'):

    if not os.path.exists(f'{address}/data/{factor_name}.npy'):
        print(time.strftime('%Y%m%d %H:%M:%S'),
              f"factor {factor_name} not found, restore factor from 20140801 instead.")
        store_factor(factor_name, 20140801, end_date, standardize_days, freq, address)
        return None

    if not amend_start_date:
        amend_start_date = np.load('%s/data/idx_date.npy' % address)[-1]

    end_date = get_recent_trade_date(end_date, dividing_point=18)
    amend_date_list = get_date_range(amend_start_date, end_date)
    amend_start_date = amend_date_list[0]
    idx_date = np.load('%s/data/idx_date.npy' % address)
    idx_code = np.load('%s/data/idx_code.npy' % address)
    end_date = get_recent_trade_date(end_date, dividing_point=18)
    before_len = idx_date[idx_date < amend_start_date].shape[0]

    factor_size = before_len * (2 * freq - 1) * 4 + 128
    update_start_date = idx_date[before_len]
    calc_start_date = get_pre_trade_date(update_start_date, standardize_days + 1)
    calc_date_list = get_date_range(calc_start_date, end_date)
    select_idx = (idx_date <= end_date) & (idx_date >= update_start_date)
    store_date = idx_date[select_idx]
    store_code = idx_code[select_idx]
    stock_pool, date_list, code_list = infer_stock_pool(store_date, store_code)

    factor = _load_pickle_frame(factor_name, calc_date_list, code_list)
    if factor.shape[0] < len(calc_date_list):
        print(time.strftime('%Y%m%d %H:%M:%S'), f"factor {factor_name} data has not arrived.")
        if factor.shape[0] <= standardize_days + 1:
            return
        else:
            miss_days = len(calc_date_list) - factor.shape[0]
            stock_pool = stock_pool[:-miss_days]
    factor, mean, std = get_std_factor(factor, standardize_days, freq, standardize_days)
    mean = mean[1:][stock_pool].astype(np.float64)
    std = std[1:][stock_pool].astype(np.float64)
    factor = np.concatenate((factor[:-1, 1:], factor[1:]), axis=1).transpose(0, 2, 1)[stock_pool].astype(
        np.float32)

    fp = np.memmap('%s/data/%s.npy' % (address, factor_name),
                   dtype='float32', mode='r+', shape=factor.shape, offset=factor_size)
    fp[:] = factor
    del fp
    gc.collect()

    mean_size = before_len * 8 + 128
    fp = np.memmap('%s/mean/%s.npy' % (address, factor_name),
                   dtype='float64', mode='r+', shape=mean.shape, offset=mean_size)
    fp[:] = mean
    del fp
    gc.collect()

    fp = np.memmap('%s/std/%s.npy' % (address, factor_name),
                   dtype='float64', mode='r+', shape=std.shape, offset=mean_size)
    fp[:] = std
    del fp
    gc.collect()

    print(time.strftime('%Y%m%d %H:%M:%S'),
          f"{factor_name} is amended from {amend_start_date} to {end_date} successfully.")

if __name__ == '__main__':

    from HFfactor.MinFactorSuper.Utility.Parallel import play_aimr
    from dataApi import aimr
    start_date1 = 20140801
    end_date1 = 20200630

    start_date2 = 0
    end_date2 = None
    # end_date2 = None

    # factor_address = '/data/group/800442/800319/HFfactor/RealTimeFixRollRobust2/data/'
    factor_address = '/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/' #amend20211126
    factor_list = sorted(get_fix_factor_list(True, factor_address))
    # init_update(restore_start_date=start_date1, end_date=end_date1, address=factor_address)

    def _func1(sub_list, line=0):
        for factor_name in sub_list:
            store_factor(factor_name, restore_start_date=start_date1, end_date=end_date1,
                         address=factor_address + '../')
    # multiprocess(24, _func1, factor_list)

    # factor_list = get_fix_factor_list(False, factor_address)
    # init_update(restore_start_date=start_date2, end_date=end_date2, address=factor_address)


    def _func2(sub_list, line=0):
        for factor_name in sub_list:
            store_factor(factor_name, restore_start_date=start_date1, end_date=end_date1,
                         address=factor_address + '../')

    # multiprocess(24, _func2, factor_list)


    def _func(factor_name):
        store_factor(factor_name, restore_start_date=start_date2, end_date=end_date2,
                     address=factor_address + '../')

    idd, parts = eval(aimr.getParam())
    play_aimr(idd, parts, _func, factor_list)

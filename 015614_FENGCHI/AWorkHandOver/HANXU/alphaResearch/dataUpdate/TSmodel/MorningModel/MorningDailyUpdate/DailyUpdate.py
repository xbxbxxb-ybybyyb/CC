import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.stockList import clean_stock_list, trans_windcode2int
from dataApi.getData import get_daily_1factor
from dataApi.tradeDate import get_recent_trade_date, get_pre_trade_date, get_date_range, trans_datetime2int
from TSmodel.MorningModel.PreprocessFactor import load_future, load_factor, standardize, winsorize, neutralize, \
    pre_ts, pre_cs, ind_double_rank, ind_dual_mean, get_morning_factor_list
from multiprocessing import Pool
from dataApi import aimr
import pandas as pd
import numpy as np
import time
import dask
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


def multidask(lines, func, iterable, *args):
    print('多线程启动')
    batches = []
    for j in range(lines):
        sub_iter = iterable[j::lines]
        batches.append(dask.delayed(func)(sub_iter, *args, j))
    result = dask.compute(batches)
    print('等待%s条线程全部完成...' % lines)
    print('多线程结束！')
    return result


def _create_factor_head(file_name, address='/data/group/800442/800319/HFfactor/MorningFactor/factor/'):
    head = [38889, 26093, 32, 20013, 22269, 20154, 27665, 22823, 23398, 32, 27721, 38738,
            39640, 32423, 32463, 27982, 19982, 37329, 34701, 30740, 31350, 38498, 32,
            37327, 21270, 37329, 34701, 32, 50, 48, 49, 55]
    head = np.array(head, dtype='int32')
    head.tofile('%s/%s.npy' % (address, file_name))


def _get_file_size(file_name, address='/data/group/800442/800319/HFfactor/MorningFactor/factor/'):
    size = os.path.getsize('%s/%s.npy' % (address, file_name))
    return size


def search_index(x, y):
    index = np.argsort(x)
    sorted_x = x[index]
    sorted_index = np.searchsorted(sorted_x, y)
    y_index = np.take(index, sorted_index, mode="clip")
    mask = x[y_index] != y
    result = np.ma.array(y_index, mask=mask, fill_value=0)
    return result


def set_ind_mv(calc_date_list, code_list, ind_type='SW'):
    if ind_type == 'SW':
        ind = get_daily_1factor('SW1', calc_date_list, code_list).values
        ind2 = get_daily_1factor('SW2', calc_date_list, code_list).values
        ind[ind == 6134] = ind2[ind == 6134]
        ind_codes = np.unique(ind)
        ind_codes = list(ind_codes[np.isfinite(ind_codes)])

    elif ind_type == 'CITICS':
        ind = get_daily_1factor('CITICS1', calc_date_list, code_list).values
        ind2 = get_daily_1factor('CITICS2', calc_date_list, code_list).values
        ind[ind == 'b10m'] = ind2[ind == 'b10m']
        ind_codes = sorted(list(set(ind.flatten()) - {np.nan}))

    elif isinstance(ind_type, pd.DataFrame):
        ind = ind_type.reindex(calc_date_list, code_list).values
        if ind.dtype is 'float':
            ind_codes = np.unique(ind)
            ind_codes = list(ind_codes[np.isfinite(ind_codes)])
        else:
            ind_codes = sorted(list(set(ind.flatten()) - {np.nan}))
    else:
        raise TypeError("ind_type must be SW, CITICS or pandas.DataFrame object")

    ind = np.r_['0,3', tuple(ind == x for x in ind_codes)]
    mv = np.log(get_daily_1factor('mkt_cap_ard', calc_date_list, code_list).values)
    mv_ind = np.r_[mv[None], ind]
    return mv_ind


def store_special_neutral(special_name, factor_list, end_date=None,
                          factor_address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    idx_date = np.load('%s/idx_date.npy' % factor_address)
    idx_code = np.load('%s/idx_code.npy' % factor_address)
    end_date = get_recent_trade_date(end_date, dividing_point=19)
    _choose = idx_date <= end_date
    idx_date = idx_date[_choose]
    idx_code = idx_code[_choose]
    stock_pool, date_list, code_list = infer_stock_pool(idx_date, idx_code)
    factors = {}
    if isinstance(factor_list, str):
        factor_list = [factor_list]
    for name in factor_list:
        factors[name] = get_daily_1factor(name, date_list, code_list).values
        if name == 'mkt_cap_ard':
            factors[name] = np.log(factors[name])
    factors = np.r_['0,3', tuple(factors[x] for x in factors)]
    factors = np.ascontiguousarray(factors[:, stock_pool].T, dtype='float32')
    np.save(f'{factor_address}/{special_name}.npy', factors)
    print(time.strftime('%Y%m%d %H:%M:%S'),
          f"{special_name} is updated from {idx_date[0]} to {end_date} successfully.")


def preprocess_factor(factor, stock_pool, method='W', mv_ind=None, special_mv_ind=None):
    special_mv_ind = special_mv_ind if special_mv_ind is not None else mv_ind
    if method == 'W':
        factor = pre_cs(factor, stock_pool, True, False, False)
    elif method == 'WC':
        factor = pre_cs(factor, stock_pool, True, True, False)
    elif method == 'WCN':
        factor = pre_cs(factor, stock_pool, True, True, True, mv_ind[1:] > 0, mv_ind[0], special_mv_ind)
    elif method == 'WCIm':
        factor = pre_cs(factor, stock_pool, True, True, False)
        factor = ind_dual_mean(factor, mv_ind[1:] > 0, stock_pool)
    elif method == 'WCIr':
        factor = pre_cs(factor, stock_pool, True, True, False)
        factor = ind_double_rank(factor, mv_ind[1:] > 0, stock_pool)
    elif re.match('^T\d{2}$', method):
        std_days = int(method[1:3])
        factor = pre_ts(factor, std_days, std_days, 6)
        factor[~ stock_pool] = np.nan
    elif re.match('^T\d{2}WC$', method):
        std_days = int(method[1:3])
        factor = pre_ts(factor, std_days, std_days, 0)
        factor = pre_cs(factor, stock_pool, True, True, False)
    elif re.match('^T\d{2}WCN$', method):
        std_days = int(method[1:3])
        factor = pre_ts(factor, std_days, std_days, 0)
        factor = pre_cs(factor, stock_pool, True, True, True, mv_ind[1:] > 0, mv_ind[0], special_mv_ind)
    elif re.match('^T\d{2}WCIm$', method):
        std_days = int(method[1:3])
        factor = pre_ts(factor, std_days, std_days, 0)
        factor = pre_cs(factor, stock_pool, True, True, False)
        factor = ind_dual_mean(factor, mv_ind[1:] > 0, stock_pool)
    elif re.match('^T\d{2}WCIr$', method):
        std_days = int(method[1:3])
        factor = pre_ts(factor, std_days, std_days, 0)
        factor = pre_cs(factor, stock_pool, True, True, False)
        factor = ind_double_rank(factor, mv_ind[1:] > 0, stock_pool)
    elif re.match('^WT\d{2}$', method):
        std_days = int(method[2:4])
        factor = pre_cs(factor, stock_pool, True, False, False)
        factor = pre_ts(factor, std_days, std_days, 6)
        factor[~ stock_pool[std_days:]] = np.nan
    elif re.match('^WCT\d{2}$', method):
        std_days = int(method[3:5])
        factor = pre_cs(factor, stock_pool, True, True, False)
        factor = pre_ts(factor, std_days, std_days, 6)
        factor[~ stock_pool[std_days:]] = np.nan
    elif re.match('^WCNT\d{2}$', method):
        std_days = int(method[4:6])
        factor = pre_cs(factor, stock_pool, True, True, True, mv_ind[1:] > 0, mv_ind[0], special_mv_ind)
        factor = pre_ts(factor, std_days, std_days, 6)
        factor[~ stock_pool[std_days:]] = np.nan
    else:
        raise ValueError("Illegal preprocess method.")
    return factor


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


def infer_nolimit_pool(idx_date, idx_code, idx_time, arr=None):
    date_list, date_i = np.unique(idx_date, return_inverse=True)
    code_list, code_i = np.unique(idx_code, return_inverse=True)
    time_list, time_i = np.unique(idx_time, return_inverse=True)
    date_list = date_list.tolist()
    code_list = code_list.tolist()
    time_list = time_list.tolist()
    nolimit_pool = np.full((date_i[-1] + 1) * (code_i[-1] + 1) * (time_i[-1] + 1), False)
    dct_i = date_i * (code_i[-1] + 1) * (time_i[-1] + 1) + code_i * (time_i[-1] + 1) + time_i
    nolimit_pool[dct_i] = True
    nolimit_pool = nolimit_pool.reshape(date_i[-1] + 1, code_i[-1] + 1, time_i[-1] + 1)
    if arr is not None:
        factor = np.full((date_i[-1] + 1) * (code_i[-1] + 1) * (time_i[-1] + 1), np.nan, dtype=arr.dtype)
        factor[dct_i] = arr
        factor = factor.reshape(date_i[-1] + 1, code_i[-1] + 1, time_i[-1] + 1)
        return nolimit_pool, date_list, code_list, time_list, factor
    else:
        return nolimit_pool, date_list, code_list, time_list


def recover_mv_ind(idx_date, start_date, end_date, stock_pool, special_name=None,
                   factor_address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    neutral_num = int(re.match('^N(\d)', special_name)[1]) if special_name else 31
    special_name = special_name if special_name else 'mv_ind'

    start_idx = idx_date.tolist().index(start_date)
    end_idx = (idx_date <= end_date).sum()
    offset = 128 + 4 * neutral_num * start_idx
    shape = (end_idx - start_idx, neutral_num)

    fp = np.memmap('%s/%s.npy' % (factor_address, special_name),
                   dtype='float32', mode='r', offset=offset, shape=shape)
    mv_ind = fp[:].T.astype(np.float64)
    del fp

    arr = np.full((neutral_num,) + stock_pool.shape, np.nan, dtype=np.float64)
    arr[:, stock_pool] = mv_ind
    if arr.shape[0] == 1:
        arr = arr[0]
    return arr


def store_risk_factor(end_date=None, factor_address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    risk_factors = [
        'Beta',
        'BookToPrice',
        'DividendYield',
        'EarningsQuality',
        'EarningsVariability',
        'EarningsYield',
        'Growth',
        'InvestmentQuality',
        'Leverage',
        'Liquidity',
        'LongTermReversal',
        'MidCapitalization',
        'Momentum',
        'Profitability',
        'ResidualVolatility',
        'Size',
    ]
    risk_address = '/data/group/800002/basic_data/full/financial_data/' \
                   'RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5'
    idx_date = np.load('%s/idx_date.npy' % factor_address)
    idx_code = np.load('%s/idx_code.npy' % factor_address)
    end_date = get_recent_trade_date(end_date, dividing_point=19)
    _choose = idx_date <= end_date
    idx_date = idx_date[_choose]
    idx_code = idx_code[_choose]
    stock_pool, date_list, code_list = infer_stock_pool(idx_date, idx_code)
    for item in risk_factors:
        factor = pd.read_hdf(risk_address, item)[item].unstack()
        factor.index = factor.index.map(trans_datetime2int)
        factor.columns = factor.columns.map(trans_windcode2int)
        factor = factor.reindex(index=date_list, columns=code_list).values.astype('float32')
        factor = np.ascontiguousarray(factor[stock_pool], dtype='float32')
        np.save(f'{factor_address}/{item}.npy', factor)
        print(time.strftime('%Y%m%d %H:%M:%S'),
              f"{item} is updated from {idx_date[0]} to {end_date} successfully.")


def update_idx(calc_start_date=0, end_date=None,
               data_address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    end_date = get_recent_trade_date(end_date, dividing_point=19)
    if os.path.exists('%s/idx_date.npy' % data_address):
        raw_idx_date = np.load('%s/idx_date.npy' % data_address)
        raw_idx_code = np.load('%s/idx_code.npy' % data_address)
    else:
        raw_idx_date = np.array([], dtype='int32')
        raw_idx_code = np.array([], dtype='int32')
    if raw_idx_date.shape[0] == 0:
        calc_start_date = 20140603
        raw_idx_date = np.array([], dtype='int32')
        raw_idx_code = np.array([], dtype='int32')
    elif (calc_start_date == 0) | (calc_start_date > raw_idx_date[-1]):
        calc_start_date = get_pre_trade_date(raw_idx_date[-1], -1)
    else:
        calc_start_date = get_recent_trade_date(calc_start_date)
        raw_idx_code = raw_idx_code[raw_idx_date < calc_start_date]
        raw_idx_date = raw_idx_date[raw_idx_date < calc_start_date]
    assert end_date >= calc_start_date
    calc_date_list = get_date_range(calc_start_date, end_date)
    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, trade_mode=False,
                                  start_date=calc_start_date, end_date=end_date)
    code_list = stock_pool.columns.to_list()
    stock_pool = stock_pool.values > 0.5
    new_idx_date = (np.array(calc_date_list)[:, None] + np.zeros(len(code_list)))[stock_pool].astype(np.int32)
    new_idx_code = (np.array(code_list)[None, :] + np.zeros((len(calc_date_list), 1)))[stock_pool].astype(np.int32)
    idx_date = np.r_[raw_idx_date, new_idx_date]
    idx_code = np.r_[raw_idx_code, new_idx_code]
    drop_offset = 128 + 4 * idx_date[idx_date < 20140801].shape[0]
    np.save('%s/idx_date.npy' % data_address, idx_date)
    np.save('%s/idx_code.npy' % data_address, idx_code)
    pd.to_pickle(drop_offset, '%s/drop_offset.pkl' % data_address)
    print(time.strftime('%Y%m%d %H:%M:%S'),
          f"idx_date is updated from {calc_start_date} to {end_date} successfully.")


def update_mv_ind(calc_start_date=0, end_date=None,
                  data_address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    idx_date = np.load('%s/idx_date.npy' % data_address)
    idx_code = np.load('%s/idx_code.npy' % data_address)
    end_date = min(get_recent_trade_date(end_date, dividing_point=19), idx_date[-1])
    if (calc_start_date == 0) | (calc_start_date > idx_date[-1]):
        calc_start_date = 20140603
    else:
        calc_start_date = max(get_recent_trade_date(calc_start_date), 20140603)
    assert end_date >= calc_start_date
    offset = 128 + 124 * idx_date[idx_date < calc_start_date].shape[0]
    use_idx_code = idx_code[(idx_date >= calc_start_date) & (idx_date <= end_date)]
    use_idx_date = idx_date[(idx_date >= calc_start_date) & (idx_date <= end_date)]
    stock_pool, date_list, code_list = infer_stock_pool(use_idx_date, use_idx_code)
    mv_ind = np.ascontiguousarray(set_ind_mv(date_list, code_list, ind_type='SW')[:, stock_pool].T, dtype='float32')
    assert mv_ind.shape[1] == 31
    if not os.path.exists(f'{data_address}/mv_ind.npy'):
        _create_factor_head('mv_ind', data_address)
    fp = np.memmap('%s/%s.npy' % (data_address, 'mv_ind'),
                   dtype='float32', mode='r+', shape=mv_ind.shape, offset=offset)
    fp[:] = mv_ind
    del fp
    print(time.strftime('%Y%m%d %H:%M:%S'),
          f"mv_ind is updated from {calc_start_date} to {end_date} successfully.")


def update_future(test_start_date=0, end_date=None, only_std=False,
                  future_type='future930t30h1d', future_std_methods='uniform10t30',
                  data_address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    idx_date = np.load('%s/idx_date.npy' % data_address)
    idx_code = np.load('%s/idx_code.npy' % data_address)
    end_date = min(get_recent_trade_date(end_date, dividing_point=19), idx_date[-1])
    if (test_start_date == 0) | (test_start_date > idx_date[-1]):
        test_start_date = 20140801
    else:
        test_start_date = max(get_recent_trade_date(test_start_date), 20140801)
    assert end_date >= test_start_date
    offset = 128 + 4 * idx_date[(idx_date < test_start_date) & (idx_date >= 20140801)].shape[0]
    use_idx_code = idx_code[(idx_date >= test_start_date) & (idx_date <= end_date)]
    use_idx_date = idx_date[(idx_date >= test_start_date) & (idx_date <= end_date)]
    stock_pool, date_list, code_list = infer_stock_pool(use_idx_date, use_idx_code)
    if only_std:
        fp = np.memmap('%s/%s.npy' % (f'{data_address}/{future_type}', 'future'),
                       dtype='float32', mode='r', shape=stock_pool.sum(), offset=offset)
        future_ = fp.__array__()
        del fp
        _, _, _, future = infer_stock_pool(use_idx_date, use_idx_code, future_)
        f_end_date = end_date
    else:
        bar_min = int(re.match('^future(\d+)t(\d+)h(\d+)(d?)', future_type)[1])
        order_keep_min = int(re.match('^future(\d+)t(\d+)h(\d+)(d?)', future_type)[2])
        future_days = re.match('^future(\d+)t(\d+)h(\d+)(d?)', future_type)[3]
        future_days = [int(x) for x in list(future_days)]
        tmr = re.match('^future(\d+)t(\d+)h(\d+)(d?)', future_type)[4] == 'd'
        if not os.path.exists(f'{data_address}/{future_type}'):
            os.makedirs(f'{data_address}/{future_type}')
        if not os.path.exists('%s/future.npy' % f'{data_address}/{future_type}'):
            _create_factor_head('future', f'{data_address}/{future_type}')
        future = load_future(date_list, code_list, future_days=future_days, bar_min=bar_min,
                             order_keep_min=order_keep_min, tmr=tmr, twap=True).astype(np.float32)
        if future.shape[0] == 0:
            print(time.strftime('%Y%m%d %H:%M:%S'), f"{future_type} no new data.")
            return
        f_end_date = date_list[future.shape[0] - 1]
        future_ = np.ascontiguousarray(future[stock_pool[:future.shape[0]]])
        fp = np.memmap('%s/%s.npy' % (f'{data_address}/{future_type}', 'future'),
                       dtype='float32', mode='r+', shape=future_.shape, offset=offset)
        fp[:] = future_
        del fp
        print(time.strftime('%Y%m%d %H:%M:%S'),
              f"{future_type} is updated from {test_start_date} to {f_end_date} successfully.")
    future_std_methods = [future_std_methods] if isinstance(future_std_methods, str) else future_std_methods
    for method in future_std_methods:
        if not os.path.exists(f'{data_address}/{future_type}/future_{method}.npy'):
            _create_factor_head(f'future_{method}', f'{data_address}/{future_type}')
        if 'uniform' in method:
            future_standardize = standardize(future, method=method)
        else:
            method_ = method
            special_mv_ind = None
            mv_ind = None
            if 'N' in method_:
                mv_ind = recover_mv_ind(idx_date, test_start_date, f_end_date, stock_pool[:future.shape[0]])
                special_name = re.search('WC(N\d[A-z][A-z0-9]+)[T]?', method_)
                special_name = special_name[1] if special_name else special_name
                if special_name:
                    method_ = method_.replace(special_name, 'N')
                    special_mv_ind = recover_mv_ind(
                        idx_date, test_start_date, f_end_date, stock_pool[:future.shape[0]], special_name)
            if 'log1p' in method:
                future_standardize = preprocess_factor(
                    np.log1p(future), stock_pool[:future.shape[0]],
                    method_.replace('log1p', ''), mv_ind, special_mv_ind)
            else:
                future_standardize = preprocess_factor(future, stock_pool[:future.shape[0]],
                                                       method_, mv_ind, special_mv_ind)
        future_standardize = np.ascontiguousarray(future_standardize[stock_pool[:future.shape[0]]], dtype='float32')
        fp = np.memmap('%s/%s.npy' % (f'{data_address}/{future_type}', f'future_{method}'),
                       dtype='float32', mode='r+', shape=future_standardize.shape, offset=offset)
        fp[:] = future_standardize
        del fp
        print(time.strftime('%Y%m%d %H:%M:%S'),
              f"{future_type}_{method} is updated from {test_start_date} to {f_end_date} successfully.")


def update_factor(test_start_date=0, end_date=None, ts_days=40,
                  factor_name='ABC', data_address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
    idx_date = np.load('%s/idx_date.npy' % data_address)
    idx_code = np.load('%s/idx_code.npy' % data_address)
    end_date = min(get_recent_trade_date(end_date, dividing_point=19), idx_date[-1])
    if (test_start_date == 0) | (test_start_date > idx_date[-1]):
        test_start_date = 20140801
    else:
        test_start_date = max(get_recent_trade_date(test_start_date), 20140801)
    assert end_date >= test_start_date
    offset = 128 + 4 * idx_date[(idx_date < test_start_date) & (idx_date >= 20140801)].shape[0]
    calc_start_date = get_pre_trade_date(test_start_date, ts_days)
    calc_idx_code = idx_code[(idx_date >= calc_start_date) & (idx_date <= end_date)]
    calc_idx_date = idx_date[(idx_date >= calc_start_date) & (idx_date <= end_date)]
    calc_stock_pool, calc_date_list, calc_code_list = infer_stock_pool(calc_idx_date, calc_idx_code)
    calc_factor = load_factor(factor_name, calc_date_list, calc_code_list)
    mv_ind = recover_mv_ind(idx_date, calc_start_date, end_date, calc_stock_pool)
    special_mv_ind = recover_mv_ind(idx_date, calc_start_date, end_date, calc_stock_pool, 'N1mv')
    stock_pool = calc_stock_pool[ts_days:]
    factor_shape = stock_pool.sum()

    factor_t40 = pre_ts(calc_factor, standardize_days=ts_days, test_drop_days=ts_days, clip=6)
    factor_t40_finite = np.isfinite(factor_t40)
    factor_t40[~ (factor_t40_finite & stock_pool)] = np.nan
    factor_t40_w = winsorize(factor_t40, method='mad', alpha=0.01)
    factor_t40_wc = standardize(factor_t40_w)
    factor_t40_wcn = neutralize(factor_t40_wc, mv_ind[1:, ts_days:] > 0, mv_ind[0, ts_days:], mv_ind[:, ts_days:],
                                stock_pool, method='ols', fill='ind_mad')
    factor_t40_wcn = standardize(factor_t40_wcn)
    factor_t40_wcim = ind_dual_mean(factor_t40_wc, mv_ind[1:, ts_days:] > 0, stock_pool)
    factor_t40_wcir = ind_double_rank(factor_t40_wc, mv_ind[1:, ts_days:] > 0, stock_pool)
    factor_t40_wcn1mv = neutralize(factor_t40_wc, mv_ind[1:, ts_days:] > 0, mv_ind[0, ts_days:],
                                   special_mv_ind[ts_days:], stock_pool, method='ols', fill='ind_mad')
    factor_t40_wcn1mv = standardize(factor_t40_wcn1mv)

    factor_finite = np.isfinite(calc_factor)
    calc_factor[~ (factor_finite & calc_stock_pool)] = np.nan
    factor_w = winsorize(calc_factor, method='mad', alpha=0.01)
    factor_wt40 = pre_ts(factor_w, standardize_days=ts_days, test_drop_days=ts_days, clip=6)
    factor_wc = standardize(factor_w)
    factor_wct40 = pre_ts(factor_wc, standardize_days=ts_days, test_drop_days=ts_days, clip=6)
    factor_wcn = neutralize(factor_wc, mv_ind[1:] > 0, mv_ind[0], mv_ind, calc_stock_pool, method='ols', fill='ind_mad')
    factor_wcn = standardize(factor_wcn)
    factor_wcnt40 = pre_ts(factor_wcn, standardize_days=ts_days, test_drop_days=ts_days, clip=6)
    factor_wcim = ind_dual_mean(factor_wc, mv_ind[1:] > 0, calc_stock_pool)
    factor_wcir = ind_double_rank(factor_wc, mv_ind[1:] > 0, calc_stock_pool)
    factor_wcn1mv = neutralize(factor_wc, mv_ind[1:] > 0, mv_ind[0], special_mv_ind,
                               calc_stock_pool, method='ols', fill='ind_mad')
    factor_wcn1mv = standardize(factor_wcn1mv)

    def _update_save_factor(method, fac):
        if not os.path.exists(f'{data_address}/factor/{method}_{factor_name}.npy'):
            _create_factor_head(f'{method}_{factor_name}', f'{data_address}/factor/')
        fp = np.memmap(f'{data_address}/factor/{method}_{factor_name}.npy',
                       dtype='float32', mode='r+', shape=factor_shape, offset=offset)
        fp[:] = np.ascontiguousarray(fac[stock_pool], dtype='float32')
        del fp
    if not os.path.exists(f'{data_address}/factor/'):
        os.makedirs(f'{data_address}/factor/')
    _update_save_factor('W', factor_w[ts_days:])
    _update_save_factor('WT40', factor_wt40)
    _update_save_factor('WC', factor_wc[ts_days:])
    _update_save_factor('WCT40', factor_wct40)
    _update_save_factor('WCN', factor_wcn[ts_days:])
    _update_save_factor('WCNT40', factor_wcnt40)
    _update_save_factor('WCIm', factor_wcim[ts_days:])
    _update_save_factor('WCIr', factor_wcir[ts_days:])
    _update_save_factor('WCN1mv', factor_wcn1mv[ts_days:])
    _update_save_factor('T40', factor_t40)
    _update_save_factor('T40WC', factor_t40_wc)
    _update_save_factor('T40WCN', factor_t40_wcn)
    _update_save_factor('T40WCIm', factor_t40_wcim)
    _update_save_factor('T40WCIr', factor_t40_wcir)
    _update_save_factor('T40WCN1mv', factor_t40_wcn1mv)
    print(time.strftime('%Y%m%d %H:%M:%S'),
          f"{factor_name} is updated from {test_start_date} to {end_date} successfully.")

if __name__ == '__main__':
    start_date = 20140603
    amend_date = 20140801
    recent_date = amend_date if amend_date else get_recent_trade_date(dividing_point=19)
    data_address = '/data/group/800442/800319/HFfactor/MorningFactor/data/'
    # future_types = [
    #     'future930t30h1d', 'future930t30h2d', 'future930t30h3d', 'future930t30h5d', 'future930t30h9d',
    #     'future930t240h1d', 'future930t240h2d', 'future930t240h3d', 'future930t240h5d', 'future930t240h9d',
    #     'future1000t210h1d', 'future1000t210h2d', 'future1000t210h3d', 'future1000t210h5d', 'future1000t210h9d',
    # ]

    # fix_future_types = [
    #     'future1000t30h1d', 'future1030t30h1d', 'future1100t30h1d', 'future1300t30h1d', 'future1330t30h1d', 'future1400t30h1d', 'future1430t30h1d',
    #     'future1000t30h2d', 'future1030t30h2d', 'future1100t30h2d', 'future1300t30h2d', 'future1330t30h2d', 'future1400t30h2d', 'future1430t30h2d',
    #     'future1000t30h2d', 'future1030t30h2d', 'future1100t30h2d', 'future1300t30h2d', 'future1330t30h2d', 'future1400t30h2d', 'future1430t30h2d',
    # ]

    future_std_methods = ['uniform', 'uniform10t30', 'uniform10t50', 'uniform20t50',
                          'WC', 'WCN', 'WCN1mv', 'log1pWC', 'log1pWCN', 'log1pWCN1mv']
    update_future(0, future_type='future930t1500h0d',
                  future_std_methods=future_std_methods, data_address=data_address)
    # factor_list = get_morning_factor_list(True) #3968
    # update_idx(recent_date, data_address=data_address)
    # update_mv_ind(recent_date, data_address=data_address)
    # store_special_neutral('N1mv', ['mkt_cap_ard'], factor_address=data_address)
    # def _func_future(sub_list, line=0):
    #     for future_name in sub_list:
    #         future_days = int(re.match('^future(\d+)t(\d+)h(\d+)(d?)', future_name)[3]) + 1
    #         update_future(get_pre_trade_date(recent_date, future_days), future_type=future_name,
    #                       future_std_methods=future_std_methods, data_address=data_address)
    #
    # def _func_fix_future(sub_list, line=0):
    #     for future_name in sub_list:
    #         future_days = int(re.match('^future(\d+)t(\d+)h(\d+)(d?)', future_name)[3]) + 1
    #         update_future(0, future_type=future_name,
    #                       future_std_methods=future_std_methods, data_address=data_address)
    # multiprocess(15, _func_future, future_types)
    # update_factor(recent_date, factor_name='W_' + factor_list[0], data_address=data_address)


    # def _func_factor(sub_list, line=0):
    #     for factor_name in sub_list:
    #         update_factor(recent_date, factor_name=factor_name, data_address=data_address)
    # multiprocess(36, _func_factor, factor_list)
    #
    # idx = int(aimr.getParam())
    # update_factor(recent_date, 20211126, factor_name=factor_list[idx])
    #
    #
    #
    # from TSmodel.MorningModel.MorningModelDataPrepare import select_factor_list2
    # factor_list1 = select_factor_list2(
    #     get_pre_trade_date(None, 6), 600, 'CS', False,
    #     '/data/group/800442/800319/HFfactor/MorningFactor/statistics/cs135d930q_period_multi_summary_corr9/'
    # ).index.to_list()
    # factor_list2 = select_factor_list2(
    #     get_pre_trade_date(None, 6), 600, 'CS', False,
    #     '/data/group/800442/800319/HFfactor/MorningFactor/statistics/cs135d930q_period_multi_summary_corr7/'
    # ).index.to_list()
    # factor_list3 = select_factor_list2(
    #     get_pre_trade_date(None, 2), 100, 'TS',
    #     '/data/group/800442/800319/HFfactor/MorningFactor/statistics/ts1d930_ic10ret_multi_summary_corr7/'
    # ).index.to_list()
    # factor_list = sorted(list(set(factor_list1) | set(factor_list2) | set(factor_list3)))
    # factor_list = sorted(list(set([x.split('_', 1)[1] for x in factor_list])))
    # factor_list = sorted(list(set(get_morning_factor_list(False)) - set(factor_list)))
    # multiprocess(36, _func_factor, factor_list)
    # _func_factor(['FM11_YOYOP'])

    # def getFileModTime(file):
    #     return time.strftime('%Y%m%d%H%M%S', time.localtime(os.path.getmtime(file)))
    # aaa = os.listdir('/data/group/800442/800319/HFfactor/MorningFactor/data/factor/')
    # for f in aaa:
    #     if int(getFileModTime(f'/data/group/800442/800319/HFfactor/MorningFactor/data/factor/{f}')) < 20211130111600:
    #         os.remove(f'/data/group/800442/800319/HFfactor/MorningFactor/data/factor/{f}')
    # bbb = [x.split('_', 1)[1][:-4] for x in os.listdir('/data/group/800442/800319/HFfactor/MorningFactor/data/factor/') if x.startswith('T40WCN1mv')]
    # factor_list = sorted(list(set(get_morning_factor_list(False)) - set(bbb)))

    # error_list = [
    #     'QfaROE',
    #     'QfaYoyeps',
    #     'RELATIVE_REPORT_NUMBER75divpreclosediff',
    #     'REPORT_NUMBER7divclosemax10',
    #     'ReportAdj',
    #     'ReportScoreGrowth',
    #     'SUNTIME_cmb_report_adjustchange60',
    #     'SUNTIME_cmb_report_adjustdiffopen',
    #     'SfaOpSur',
    #     'ShoutCutILLIQ_10',
    #     'SwingResVola0p5_trans3Day',
    #     'SwingSplit',
    #     'TickFactor_ActSellVwapStdRatio',
    #     'TickFactor_BuyOrderStd',
    #     'Tick_DownVolSellSM',
    #     'Tick_DownVolSellSkew',
    #     'Tick_bsdiff_hl_tail_passive_orderamt_corr3_daily',
    #     'Tick_bsdiff_hl_top_active_ordervol_cov1_daily',
    #     'Tick_bsdiffmktstate_amt_std_top_active_ordervol_corr3_daily',
    #     'Tick_bsdiffmktstate_idxmadiff_tail_accamount_corr3_daily',
    #     'TradeCloseInv',
    #     'TradeDiffBuySellKurt40dStd',
    #     'TurnStaD',
    #     'TurnoverSharpe',
    #     'VolPriceRunner',
    #     'VolRPriceRCorr20d',
    #     'WIRetStdAdj_WithoutBeta',
    #     'WQ016',
    #     'alp3_alpuniv',
    #     'alphas_dongj_pct_chg_swing_combine',
    #     'df29',
    #     'df3',
    #     'fund_q4',
    #     'fund_q5',
    #     'tptpchg_alpuniv',
    #     'trade_strength_last15_r20_nis',
    #     'yzhan_b_21031503_15',
    #     'yzhan_b_21031503_38',
    #     'yzhan_expr5_21052600_297',
    #     'yzhan_expr5_21052600_355',
    #     'yzhan_fi_21022400_3',
    #     'yzhan_fi_21022400_50',
    #     'yzhan_fiexpr1_21060400_281',
    #     'yzhan_fiexpr1_21060400_288',
    #     'yzhan_mf2_21071400_39',
    #     'yzhan_mf2_21071400_4',
    #     'yzhan_taq_21012601_5',
    #     'yzhan_taq_21012603_3',
    #     'yzhan_tick_21021201_98',
    #     'yzhan_tick_21021801_169',
    #     'zhy_factor_22',
    #     'zhy_factor_24',
    #     'zhy_factor_6',
    #     'zhy_factor_60',
    #     'ztwdaily1929',
    #     'ztwdaily1942'
    # ]
    #
    # load_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
    # for name in error_list:
    #     df = pd.read_pickle('%s/%s.pkl' % (load_address, name))
    #     print(name, len(df.loc['20220117'].dropna()), len(df.loc['20220118'].dropna()))
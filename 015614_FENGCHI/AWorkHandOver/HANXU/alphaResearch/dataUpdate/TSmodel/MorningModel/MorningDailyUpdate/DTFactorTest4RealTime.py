import sys

sys.path.append('/data/user/015836/HANXU/alphaResearch/dataUpdate/')
import os
import re
import time
from multiprocessing import Pool

import bottleneck
import gc
import numpy as np
import pandas as pd
import scipy.stats as sps

from TSmodel.MorningModel.DailyUpdate import infer_stock_pool, recover_mv_ind
from TSmodel.MorningModel.PreprocessFactor import corrcoef, stats_range, calc_corr, get_morning_factor_list
from dataApi import aimr
from dataApi.tradeDate import get_date_range, get_sub_date_index


def _fill(arr, l, axis=0):
    if arr.ndim == 2:
        return np.pad(arr, ((l, 0), (0, 0)), mode='constant', constant_values=np.nan)
    elif arr.ndim == 3:
        if axis:
            return np.pad(arr, ((0, 0), (l, 0), (0, 0)), mode='constant', constant_values=np.nan)
        else:
            return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)
    else:
        raise ValueError


def calc_ind_beta(X, y, axis=-1):
    X = X.copy()
    y = y.copy()
    finite = np.isfinite(y) & np.isfinite(X).all(axis=0)
    X[:, ~ finite] = np.nan
    y[~ finite] = np.nan
    X = X - np.nanmean(X, axis=axis)[..., None]
    y = y - np.nanmean(y, axis=axis)[:, None]
    multi = np.nanmean(X * y, axis=axis) / (np.nanvar(X, axis=axis))
    multi[np.isinf(multi)] = np.nan
    return multi


def calc_style_corr(X, y, axis=-1):
    X = X.copy()
    y = y.copy()
    finite = np.isfinite(y) & np.isfinite(X).all(axis=0)
    X[:, ~ finite] = np.nan
    y[~ finite] = np.nan
    X = X - np.nanmean(X, axis=axis)[..., None]
    y = y - np.nanmean(y, axis=axis)[:, None]
    multi = np.nanmean(X * y, axis=axis) / (np.nanstd(X, axis=axis) * np.nanstd(y, axis=axis))
    multi[np.isinf(multi)] = np.nan
    return multi


def dt_rank(x, m4):
    n = np.isfinite(x)
    cn = bottleneck.move_sum(n.astype('float32'), m4, axis=0)
    x = np.where(~ n, np.array([-np.inf], dtype='float32'), x)
    mx = bottleneck.move_rank(x, m4, axis=0)
    mx = ((mx + 1) * (m4 - 1) / 2 - m4 + cn) / (cn - 1)
    mx = np.where((cn < 4) | ~ n, np.array([np.nan], dtype='float32'), mx)
    return mx


def back_factor(name, standard_method, test_choose, stock_pool,
                address='/data/group/800442/800319/HFfactor/MorningFactor/data/factor/'):
    factor_name = f'{standard_method}_{name}' if standard_method is not None else name
    fp = np.memmap(f'{address}/{factor_name}.npy', dtype='float32', mode='r', offset=128)
    shape = min(fp.shape[0], test_choose.shape[0])
    data = fp[:shape][test_choose[:shape]]
    del fp
    factor = np.full_like(stock_pool, dtype=np.float32, fill_value=np.nan)
    factor[stock_pool] = data
    return factor


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


class TSFactorTest(object):
    def __init__(self, start_date=20140801, end_date=20211031,
                 address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        date_num = len(date_list)
        _idx_code = np.load(f'{address}/idx_code.npy')
        _idx_date = np.load(f'{address}/idx_date.npy')
        idx_code = _idx_code[_idx_date >= 20140801]
        idx_date = _idx_date[_idx_date >= 20140801]
        choose = (idx_date >= start_date) & (idx_date <= end_date)
        idx_code = idx_code[choose]
        idx_date = idx_date[choose]
        stock_pool, date_list, code_list = infer_stock_pool(idx_date, idx_code)
        code_num = len(code_list)

        month_split = get_sub_date_index(date_list, 'M')
        year_split = get_sub_date_index(date_list, 'Y')
        month_starts, month_ends = stats_range(month_split, date_list)
        year_starts, year_ends = stats_range(year_split, date_list)
        month_days = np.diff(np.r_[month_split, len(date_list)])
        year_days = np.diff(np.r_[year_split, len(date_list)])
        month_tags = month_ends // 100
        year_tags = year_ends // 10000

        self.date_list = date_list
        self.idx_date = _idx_date
        self.start_date = start_date
        self.end_date = end_date
        self.date_num = date_num
        self.choose = choose
        self.stock_pool = stock_pool
        self.code_list = code_list
        self.code_num = code_num
        self.address = address

        self.month_tags = month_tags
        self.year_tags = year_tags
        self.month_days = month_days
        self.year_days = year_days
        self.month_split = month_split
        self.year_split = year_split

    def set_basic_data(self, future_type, multi_future=True,
                       address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
        if multi_future:
            future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
            future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]
        else:
            future_type = [future_type]
        fp = np.memmap('%s/%s.npy' % (f'{address}/{future_type[-1]}', 'future'),
                       dtype='float32', mode='r', offset=128)
        shape = min(fp.shape[0], self.choose.shape[0])
        shape0 = self.choose[:shape].sum()
        future = np.empty((len(future_type), shape0), dtype=np.float32)
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address}/{f}/future.npy', dtype='float32', mode='r', offset=128)
            shape = min(fp.shape[0], self.choose.shape[0])
            future[j] = fp[:shape][self.choose[:shape]]
            del fp
        future = future.mean(axis=0)
        future_ = np.full_like(self.stock_pool, dtype=np.float32, fill_value=np.nan)
        future_[self.stock_pool] = future
        future = future_
        future_finite = np.isfinite(future)
        future[~ future_finite] = np.nan
        future_med = np.nanmedian(future, axis=-1)
        future_active = future - future_med[:, None]
        code_valid_num = future_finite.sum(axis=1)
        future_rank = bottleneck.nanrankdata(future, axis=-1) / code_valid_num[:, None]
        self.future = future
        self.future_med = future_med
        self.future_rank = future_rank
        self.future_active = future_active
        self.future_finite = future_finite
        self.code_valid_num = code_valid_num

    def set_factor(self, name, standard_method=None, address=None):
        if isinstance(name, np.ndarray):
            return name
        else:
            address = f'{self.address}/factor/' if address is None else address
            factor = back_factor(name, standard_method, self.choose, self.stock_pool, address)
            return factor

    def reduce_icir(self, arr, sample_min=10):
        finite = np.isfinite(arr)
        arr[~ finite] = 0
        finite = finite.astype('float32')
        arr2 = arr ** 2
        finite = finite.sum(axis=tuple(range(1, arr.ndim)))

        finite_month = np.add.reduceat(finite, self.month_split)
        finite_year = np.add.reduceat(finite, self.year_split)
        finite_total = finite.sum()
        finite_month[finite_month < sample_min] = np.nan
        finite_year[finite_year < sample_min] = np.nan

        arr_total = arr.sum()
        arrp = (arr > 0).astype('float32').sum(axis=tuple(range(1, arr.ndim)))
        arrp_month = np.add.reduceat(arrp, self.month_split)
        arrp_year = np.add.reduceat(arrp, self.year_split)
        arrp_total = arrp.sum()

        arr = arr.sum(axis=tuple(range(1, arr.ndim)))
        arr_month = np.add.reduceat(arr, self.month_split)
        arr_year = np.add.reduceat(arr, self.year_split)

        arr2 = arr2.sum(axis=tuple(range(1, arr2.ndim)))
        arr2_month = np.add.reduceat(arr2, self.month_split)
        arr2_year = np.add.reduceat(arr2, self.year_split)
        arr2_total = arr2.sum()

        std_month = ((arr2_month - arr_month ** 2 / finite_month) / (finite_month - 1)) ** 0.5
        std_year = ((arr2_year - arr_year ** 2 / finite_year) / (finite_year - 1)) ** 0.5
        std_total = ((arr2_total - arr_total ** 2 / finite_total) / (finite_total - 1)) ** 0.5

        ir_month = arr_month / finite_month / std_month * 244 ** 0.5
        ir_year = arr_year / finite_year / std_year * 244 ** 0.5
        ir_total = arr_total / finite_total / std_total * 244 ** 0.5

        ic_month = arr_month / finite_month
        ic_year = arr_year / finite_year
        ic_total = arr_total / finite_total

        pos_month = arrp_month / finite_month
        pos_year = arrp_year / finite_year
        pos_total = arrp_total / finite_total

        return ic_month, ic_year, ic_total, ir_month, ir_year, ir_total, \
               pos_month, pos_year, pos_total, finite_month, finite_year, finite_total

    def reduce_sum(self, arr):
        arr_month = np.add.reduceat(arr, self.month_split, axis=0)
        arr_year = np.add.reduceat(arr, self.year_split, axis=0)
        arr_total = arr.sum(axis=0)
        return arr_month, arr_year, arr_total

    def ts_test(self, factor):
        factor = factor.copy()
        future = self.future.copy()
        x = factor
        y = future
        n = self.future_finite
        x[~ (n & np.isfinite(x))] = 0
        y[~ n] = 0
        x2 = x ** 2
        y2 = y ** 2
        xy = x * y

        d2x, d1x, d0x = self.reduce_sum(x)
        d2y, d1y, d0y = self.reduce_sum(y)
        d2x2, d1x2, d0x2 = self.reduce_sum(x2)
        d2y2, d1y2, d0y2 = self.reduce_sum(y2)
        d2xy, d1xy, d0xy = self.reduce_sum(xy)
        d2n, d1n, d0n = self.reduce_sum(n)

        ic_all_d = calc_corr(d0x, d0y, d0x2, d0y2, d0xy, d0n)
        ic_year_d = calc_corr(d1x, d1y, d1x2, d1y2, d1xy, d1n)
        ic_month_d = calc_corr(d2x, d2y, d2x2, d2y2, d2xy, d2n)

        ic_all_d[d0n < self.date_num / 2] = np.nan
        ic_year_d[d1n < self.year_days[:, None] / 2] = np.nan
        ic_month_d[d2n < self.month_days[:, None] / 2] = np.nan

        ic_all_d_mean = np.nanmean(ic_all_d)
        ic_all_d_std = np.nanstd(ic_all_d, ddof=1)
        ic_all_d_num = np.isfinite(ic_all_d).sum()
        ic_all_d_t = ic_all_d_mean / ic_all_d_std * 244 ** 0.5
        ic_all_d_pos = (ic_all_d > 0).sum() / ic_all_d_num

        ic_year_d_mean = np.nanmean(ic_year_d, axis=1)
        ic_year_d_std = np.nanstd(ic_year_d, axis=1)
        ic_year_d_num = np.isfinite(ic_year_d).sum(axis=1)
        ic_year_d_t = ic_year_d_mean / ic_year_d_std * 244 ** 0.5
        ic_year_d_pos = (ic_year_d > 0).sum(axis=1) / ic_year_d_num

        ic_month_d_mean = np.nanmean(ic_month_d, axis=1)
        ic_month_d_std = np.nanstd(ic_month_d, axis=1)
        ic_month_d_num = np.isfinite(ic_month_d).sum(axis=1)
        ic_month_d_t = ic_month_d_mean / ic_month_d_std * 244 ** 0.5
        ic_month_d_pos = (ic_month_d > 0).sum(axis=1) / ic_month_d_num

        factor[~ self.future_finite] = np.nan
        factor *= np.sign(ic_all_d_mean)
        factor_rank = dt_rank(factor, 60) > 0.95
        factor_ret = self.future.copy()
        factor_ret[~ (self.future_finite & factor_rank)] = np.nan

        ret_month, ret_year, ret_total, ret_t_month, ret_t_year, ret_t_total, \
        ret_pos_month, ret_pos_year, ret_pos_total, ret_num_month, ret_num_year, \
        ret_num_total = self.reduce_icir(factor_ret)

        result = dict(
            ic_all_d_mean=ic_all_d_mean,
            ic_all_d_num=ic_all_d_num,
            ic_all_d_t=ic_all_d_t,
            ic_all_d_pos=ic_all_d_pos,
            ret_total=ret_total,
            ret_t_total=ret_t_total,
            ret_pos_total=ret_pos_total,
            ret_num_total=ret_num_total,

            ic_year_d_mean=ic_year_d_mean,
            ic_year_d_num=ic_year_d_num,
            ic_year_d_t=ic_year_d_t,
            ic_year_d_pos=ic_year_d_pos,
            ret_year=ret_year,
            ret_t_year=ret_t_year,
            ret_pos_year=ret_pos_year,
            ret_num_year=ret_num_year,

            ic_month_d_mean=ic_month_d_mean,
            ic_month_d_num=ic_month_d_num,
            ic_month_d_t=ic_month_d_t,
            ic_month_d_pos=ic_month_d_pos,
            ret_month=ret_month,
            ret_t_month=ret_t_month,
            ret_pos_month=ret_pos_month,
            ret_num_month=ret_num_month,

            month_tags=self.month_tags,
            year_tags=self.year_tags,
            month_days=self.month_days,
            year_days=self.year_days
        )
        return result


class CSFactorTest(object):
    def __init__(self, start_date=20140801, end_date=20211031,
                 address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        date_num = len(date_list)
        _idx_code = np.load(f'{address}/idx_code.npy')
        _idx_date = np.load(f'{address}/idx_date.npy')
        idx_code = _idx_code[_idx_date >= 20140801]
        idx_date = _idx_date[_idx_date >= 20140801]
        choose = (idx_date >= start_date) & (idx_date <= end_date)
        idx_code = idx_code[choose]
        idx_date = idx_date[choose]
        stock_pool, date_list, code_list = infer_stock_pool(idx_date, idx_code)
        code_num = len(code_list)

        month_split = get_sub_date_index(date_list, 'M')
        year_split = get_sub_date_index(date_list, 'Y')
        month_starts, month_ends = stats_range(month_split, date_list)
        year_starts, year_ends = stats_range(year_split, date_list)
        month_days = np.diff(np.r_[month_split, len(date_list)])
        year_days = np.diff(np.r_[year_split, len(date_list)])
        month_tags = month_ends // 100
        year_tags = year_ends // 10000

        self.date_list = date_list
        self.idx_date = _idx_date
        self.start_date = start_date
        self.end_date = end_date
        self.date_num = date_num
        self.choose = choose
        self.stock_pool = stock_pool
        self.code_list = code_list
        self.code_num = code_num
        self.address = address

        self.month_tags = month_tags
        self.year_tags = year_tags
        self.month_days = month_days
        self.year_days = year_days
        self.month_split = month_split
        self.year_split = year_split

    def set_basic_data(self, future_type, multi_future=True,
                       address='/data/group/800442/800319/HFfactor/MorningFactor/data/'):
        mv_ind = recover_mv_ind(self.idx_date, self.start_date, self.end_date, self.stock_pool, None, address)
        ind = mv_ind[1:] > 0
        mv = mv_ind[0]
        Beta = back_factor('Beta', None, self.choose, self.stock_pool, self.address)
        BookToPrice = back_factor('BookToPrice', None, self.choose, self.stock_pool, self.address)
        DividendYield = back_factor('DividendYield', None, self.choose, self.stock_pool, self.address)
        EarningsQuality = back_factor('EarningsQuality', None, self.choose, self.stock_pool, self.address)
        EarningsVariability = back_factor('EarningsVariability', None, self.choose, self.stock_pool, self.address)
        EarningsYield = back_factor('EarningsYield', None, self.choose, self.stock_pool, self.address)
        Growth = back_factor('Growth', None, self.choose, self.stock_pool, self.address)
        InvestmentQuality = back_factor('InvestmentQuality', None, self.choose, self.stock_pool, self.address)
        Leverage = back_factor('Leverage', None, self.choose, self.stock_pool, self.address)
        Liquidity = back_factor('Liquidity', None, self.choose, self.stock_pool, self.address)
        LongTermReversal = back_factor('LongTermReversal', None, self.choose, self.stock_pool, self.address)
        MidCapitalization = back_factor('MidCapitalization', None, self.choose, self.stock_pool, self.address)
        Momentum = back_factor('Momentum', None, self.choose, self.stock_pool, self.address)
        Profitability = back_factor('Profitability', None, self.choose, self.stock_pool, self.address)
        ResidualVolatility = back_factor('ResidualVolatility', None, self.choose, self.stock_pool, self.address)
        Size = back_factor('Size', None, self.choose, self.stock_pool, self.address)
        style_factor = np.r_['0,3', Beta, BookToPrice, DividendYield, EarningsQuality, EarningsVariability,
                             EarningsYield, Growth, InvestmentQuality, Leverage, Liquidity, LongTermReversal,
                             MidCapitalization, Momentum, Profitability, Profitability, ResidualVolatility, Size, mv]
        if multi_future:
            future_type = re.match('^(future\d+t\d+h)(\d+)(d?)', future_type)
            future_type = [future_type[1] + x + future_type[3] for x in list(future_type[2])]
        else:
            future_type = [future_type]
        fp = np.memmap('%s/%s.npy' % (f'{address}/{future_type[-1]}', 'future'),
                       dtype='float32', mode='r', offset=128)
        shape = min(fp.shape[0], self.choose.shape[0])
        shape0 = self.choose[:shape].sum()
        future = np.empty((len(future_type), shape0), dtype=np.float32)
        for j, f in enumerate(future_type):
            fp = np.memmap(f'{address}/{f}/future.npy', dtype='float32', mode='r', offset=128)
            shape = min(fp.shape[0], self.choose.shape[0])
            future[j] = fp[:shape][self.choose[:shape]]
            del fp
        future = future.mean(axis=0)
        future_ = np.full_like(self.stock_pool, dtype=np.float32, fill_value=np.nan)
        future_[self.stock_pool] = future
        future = future_
        future_finite = np.isfinite(future)
        ind[future_finite & ~ np.isfinite(ind)] = 0
        ind[:, ~ future_finite] = np.nan
        future[~ future_finite] = np.nan
        future_med = np.nanmedian(future, axis=-1)
        future_active = future - future_med[:, None]
        code_valid_num = future_finite.sum(axis=1)
        future_rank = bottleneck.nanrankdata(future, axis=-1) / code_valid_num[:, None]
        self.future = future
        self.future_med = future_med
        self.future_rank = future_rank
        self.future_active = future_active
        self.future_finite = future_finite
        self.code_valid_num = code_valid_num
        self.ind = ind
        self.style_factor = style_factor

    def set_factor(self, name, standard_method=None, address=None):
        if isinstance(name, np.ndarray):
            return name
        else:
            address = f'{self.address}/factor/' if address is None else address
            factor = back_factor(name, standard_method, self.choose, self.stock_pool, address)
            return factor

    def reduce_ic(self, arr, sample_min=10):
        finite = np.isfinite(arr)
        arr[~ finite] = 0
        finite = finite.astype('float32')
        finite = finite.sum(axis=tuple(range(1, arr.ndim)))
        finite_month = np.add.reduceat(finite, self.month_split)
        finite_year = np.add.reduceat(finite, self.year_split)
        finite_total = finite.sum()
        finite_month[finite_month < sample_min] = np.nan
        finite_year[finite_year < sample_min] = np.nan
        arr = arr.sum(axis=tuple(range(1, arr.ndim)))
        arr_month = np.add.reduceat(arr, self.month_split)
        arr_year = np.add.reduceat(arr, self.year_split)
        arr_total = arr.sum()
        arr_month /= finite_month
        arr_year /= finite_year
        arr_total /= finite_total
        return arr_month, arr_year, arr_total

    def reduce_icir(self, arr, sample_min=10):
        finite = np.isfinite(arr)
        arr[~ finite] = 0
        finite = finite.astype('float32')
        arr2 = arr ** 2
        finite = finite.sum(axis=tuple(range(1, arr.ndim)))

        finite_month = np.add.reduceat(finite, self.month_split)
        finite_year = np.add.reduceat(finite, self.year_split)
        finite_total = finite.sum()
        finite_month[finite_month < sample_min] = np.nan
        finite_year[finite_year < sample_min] = np.nan

        arr_total = arr.sum()
        arrp = (arr > 0).astype('float32').sum(axis=tuple(range(1, arr.ndim)))
        arrp_month = np.add.reduceat(arrp, self.month_split)
        arrp_year = np.add.reduceat(arrp, self.year_split)
        arrp_total = arrp.sum()

        arr = arr.sum(axis=tuple(range(1, arr.ndim)))
        arr_month = np.add.reduceat(arr, self.month_split)
        arr_year = np.add.reduceat(arr, self.year_split)

        arr2 = arr2.sum(axis=tuple(range(1, arr2.ndim)))
        arr2_month = np.add.reduceat(arr2, self.month_split)
        arr2_year = np.add.reduceat(arr2, self.year_split)
        arr2_total = arr2.sum()

        std_month = ((arr2_month - arr_month ** 2 / finite_month) / (finite_month - 1)) ** 0.5
        std_year = ((arr2_year - arr_year ** 2 / finite_year) / (finite_year - 1)) ** 0.5
        std_total = ((arr2_total - arr_total ** 2 / finite_total) / (finite_total - 1)) ** 0.5

        ir_month = arr_month / finite_month / std_month * 244 ** 0.5
        ir_year = arr_year / finite_year / std_year * 244 ** 0.5
        ir_total = arr_total / finite_total / std_total * 244 ** 0.5

        ic_month = arr_month / finite_month
        ic_year = arr_year / finite_year
        ic_total = arr_total / finite_total

        pos_month = arrp_month / finite_month
        pos_year = arrp_year / finite_year
        pos_total = arrp_total / finite_total

        return ic_month, ic_year, ic_total, ir_month, ir_year, ir_total, \
               pos_month, pos_year, pos_total, finite_month, finite_year, finite_total

    def reduce_sum(self, arr):
        arr_month = np.add.reduceat(arr, self.month_split, axis=0)
        arr_year = np.add.reduceat(arr, self.year_split, axis=0)
        arr_total = arr.sum(axis=0)
        return arr_month, arr_year, arr_total

    def cs_test(self, factor, groups=10):
        factor = factor.copy()
        complete = ((self.future_finite & np.isfinite(factor)).sum(axis=1) / self.code_valid_num)
        factor[self.future_finite & ~ np.isfinite(factor)] = 0
        factor[~ self.future_finite] = np.nan
        factor_mean = np.nanmean(factor, axis=1)
        factor_std = np.nanstd(factor, axis=1, ddof=1)
        factor_med = np.nanmedian(factor, axis=1)
        factor_skew = np.full(self.date_num, np.nan)
        factor_kurt = np.full(self.date_num, np.nan)
        if ((complete * self.code_valid_num > 3) & (factor_std > 0)).sum() > 0:
            factor_skew[(complete * self.code_valid_num > 3) & (factor_std > 0)] = sps.skew(
                factor[(complete * self.code_valid_num > 3) & (factor_std > 0)],
                axis=1, bias=False, nan_policy='omit').data
            factor_kurt[(complete * self.code_valid_num > 3) & (factor_std > 0)] = sps.kurtosis(
                factor[(complete * self.code_valid_num > 3) & (factor_std > 0)],
                axis=1, fisher=True, bias=False, nan_policy='omit').data
        factor_mad = np.nanmedian(factor - factor_med[:, None], axis=1)
        factor_min = np.nanmin(factor, axis=1)
        factor_max = np.nanmax(factor, axis=1)
        factor_q005 = np.nanquantile(factor, 0.005, axis=1)
        factor_q01 = np.nanquantile(factor, 0.01, axis=1)
        factor_q25 = np.nanquantile(factor, 0.25, axis=1)
        factor_q75 = np.nanquantile(factor, 0.75, axis=1)
        factor_q99 = np.nanquantile(factor, 0.99, axis=1)
        factor_q995 = np.nanquantile(factor, 0.995, axis=1)
        factor_mvmax = factor_mean + factor_std * 3
        factor_mvmin = factor_mean - factor_std * 3
        factor_madmax = factor_med + factor_mad * 4.449
        factor_madmin = factor_med - factor_mad * 4.449
        style_expose = calc_style_corr(self.style_factor, factor)
        ind_expose = calc_ind_beta(self.ind, factor)
        ind_expose = np.nansum(self.ind * ind_expose[..., None], axis=0)
        ind_expose = corrcoef(factor, ind_expose)
        factor_rank = bottleneck.nanrankdata(factor, axis=-1) / self.code_valid_num[:, None]
        factor_group = np.ceil(factor_rank * groups)
        IC = corrcoef(factor, self.future_active)
        rank_IC = corrcoef(factor_rank, self.future_rank)
        group_active = np.c_['0,2', tuple(np.ma.array(self.future_active, mask=np.isnan(self.future_active) | (
                factor_group != x)).mean(axis=-1).data for x in range(1, groups + 1))].T
        group_turn = np.c_['0,2', tuple(np.ma.array(_fill(factor_group[:-1], 1) != x, mask=np.isnan(
            self.future_active) | (factor_group != x)).mean(axis=-1).data for x in range(1, groups + 1))].T
        group_turn[:1] = np.nan
        group_rank = bottleneck.nanrankdata(group_active, axis=1)
        group_rank_valid = group_rank.max(axis=1) == groups
        group_IC = np.nanmean((group_rank - (groups + 1) / 2) * (np.arange(1, groups + 1) - (
                groups + 1) / 2), axis=1) / np.nanstd(group_rank, axis=1) / np.nanstd(np.arange(1, groups + 1))
        group_pos_dist = ((group_rank - np.arange(1, groups + 1)[None, :]) ** 2).sum(axis=1) / groups
        group_neg_dist = ((group_rank - np.arange(1, groups + 1)[None, ::-1]) ** 2).sum(axis=1) / groups
        group_IC[~ group_rank_valid] = 0
        group_pos_dist[~ group_rank_valid] = np.nan
        group_neg_dist[~ group_rank_valid] = np.nan
        group_active[~ group_rank_valid, :] = np.nan
        group_turn[~ group_rank_valid, :] = np.nan
        group_turn[np.r_[True, ~group_rank_valid[:-1]], :] = np.nan
        result = np.r_['0,2', self.date_list, self.future_med, complete,
                       factor_mean, factor_std, factor_skew, factor_kurt, factor_q25, factor_med,
                       factor_q75, factor_min, factor_q005, factor_q01, factor_mvmin, factor_madmin,
                       factor_max, factor_q995, factor_q99, factor_mvmax, factor_madmax, IC, rank_IC,
                       group_IC, group_pos_dist, group_neg_dist, ind_expose]
        result = np.r_[result, style_expose, group_active.T, group_turn.T].T
        return result




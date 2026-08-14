import os
import re
import pandas as pd
import numpy as np
import bottleneck
from tqdm import tqdm
from numba import jit
from scipy.stats import norm, boxcox
from multiprocessing import Pool
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_daily_1factor, get_daily_1day
from dataApi.stockList import clean_stock_list, trans_windcode2int

def multiprocess(lines, func, iterable, *args):

    pool = Pool(processes=lines)
    print('多进程启动')
    pool_apply_async = {}
    parts = len(iterable) // lines
    remainder = len(iterable) % lines
    iter_start = 0
    for j in range(lines):
        if remainder > 0:
            iter_end = iter_start + parts + 1
            remainder -= 1
        else:
            iter_end = iter_start + parts
        sub_iter = iterable[iter_start: iter_end]
        pool.apply_async(func, (sub_iter, ) + args + (j, ))
        iter_start = iter_end
    pool.close()
    print('等待%s个进程全部完成...' % lines)
    pool.join()
    print('多进程结束！')
    return pool_apply_async

def load_factor(date, factor_address, factor_list, code_list=None):

    file_name = os.listdir('%s/mddate=%s' % (factor_address, date))[0]
    df = pd.read_parquet('%s/mddate=%s/%s' % (factor_address, date, file_name), columns=['stock'] + factor_list)
    df.set_index('stock', inplace=True)
    df.index = df.index.map(trans_windcode2int)
    if code_list is not None:
        return df.reindex(code_list).T
    else:
        return df.T

def winsorize(arr, axis=-1, method='mad', out='raw_rank', alpha=0.01):

    if method == 'mad':
        arr = arr.swapaxes(0, axis).astype(float)
        arr_nan = np.isnan(arr)
        median = np.nanmedian(arr, axis=0)
        arr[(np.sum(arr == median, axis=0) / (~arr_nan).sum(axis=0) >= 0.5) & (arr == median)] = np.nan
        arr_nan = np.isnan(arr)
        median = np.nanmedian(arr, axis=0)
        mad = np.nanmedian(np.abs(arr - median), axis=0)
        arr_count = (~ arr_nan).sum(axis=0)
        up_bound = median + 4.449 * mad
        down_bound = median - 4.449 * mad

        Q99 = np.nanpercentile(arr, (1 - alpha) * 100, axis=0)
        Q01 = np.nanpercentile(arr, alpha * 100, axis=0)
        up_bound = np.where(up_bound > Q99, up_bound, Q99)
        down_bound = np.where(down_bound < Q01, down_bound, Q01)

        up_mask = (arr <= up_bound) | arr_nan
        down_mask = (arr >= down_bound) | arr_nan
        arr_up = np.ma.array(arr, mask=up_mask, fill_value=np.nan)
        arr_down = np.ma.array(arr, mask=down_mask, fill_value=np.nan)
        up_count = arr_up.count(axis=0)
        down_count = arr_down.count(axis=0)
        if out == 'pct':
            return np.r_['0,2', up_count / arr_count, down_count / arr_count]

        elif out == 'raw_rank':
            arr[~ up_mask] = (up_bound + 0.1483 * mad * bottleneck.nanrankdata(
                arr_up.filled(), axis=0) / up_count)[~ up_mask]
            arr[~ down_mask] = (down_bound - 0.1483 * mad * (1 + (1 - bottleneck.nanrankdata(
                arr_down.filled(), axis=0)) / down_count))[~ down_mask]

        elif out == 'raw':
            arr[~ up_mask] = up_bound.repeat(arr.shape[0]).reshape(arr.T.shape).T[~ up_mask]
            arr[~ down_mask] = down_bound.repeat(arr.shape[0]).reshape(arr.T.shape).T[~ down_mask]

        elif out == 'short':
            arr[~ up_mask] = np.nan
            arr[~ down_mask] = np.nan
        else:
            raise ValueError("param out must be pct, raw or short.")
        arr = arr.swapaxes(0, axis)
        return arr

    elif method == 'mv':
        arr = arr.swapaxes(0, axis).astype(float)
        arr_nan = np.isnan(arr)
        arr_count = (~ arr_nan).sum(axis=0)
        mean = np.nanmean(arr, axis=0)
        std = np.nanstd(arr, ddof=1, axis=0)
        up_bound = mean + 3 * std
        down_bound = mean - 3 * std

        Q99 = np.nanpercentile(arr, (1 - alpha) * 100, axis=0)
        Q01 = np.nanpercentile(arr, alpha * 100, axis=0)
        up_bound = np.where(up_bound > Q99, up_bound, Q99)
        down_bound = np.where(down_bound < Q01, down_bound, Q01)

        up_mask = (arr <= up_bound) | arr_nan
        down_mask = (arr >= down_bound) | arr_nan
        arr_up = np.ma.array(arr, mask=up_mask, fill_value=np.nan)
        arr_down = np.ma.array(arr, mask=down_mask, fill_value=np.nan)
        up_count = arr_up.count(axis=0)
        down_count = arr_down.count(axis=0)
        if out == 'pct':
            return np.r_['0,2', up_count / arr_count, down_count / arr_count]

        elif out == 'raw_rank':
            arr[~ up_mask] = (up_bound + 0.1 * std * bottleneck.nanrankdata(
                arr_up.filled(), axis=0) / up_count)[~ up_mask]
            arr[~ down_mask] = (down_bound - 0.1 * std * (1 + (1 - bottleneck.nanrankdata(
                arr_down.filled(), axis=0)) / down_count))[~ down_mask]

        elif out == 'raw':
            arr[~ up_mask] = up_bound.repeat(arr.shape[0]).reshape(arr.T.shape).T[~ up_mask]
            arr[~ down_mask] = down_bound.repeat(arr.shape[0]).reshape(arr.T.shape).T[~ down_mask]

        elif out == 'short':
            arr[~ up_mask] = np.nan
            arr[~ down_mask] = np.nan
        else:
            raise ValueError("param out must be pct, raw or short.")
        arr = arr.swapaxes(0, axis)
        return arr

    elif method =='box':

        def _calc_mc(x, med):

            xi = np.ma.compressed(np.ma.array(x, mask=(x > med) | (np.isnan(x))))
            xj = np.ma.compressed(np.ma.array(x, mask=(x < med) | (np.isnan(x))))
            kernel = np.add.outer(xj, xi)
            kernel -= 2 * med
            kernel /= np.subtract.outer(xj, xi)
            return np.nanmedian(kernel)

        arr = arr.swapaxes(0, axis).astype(float)
        arr_nan = np.isnan(arr)
        arr_count = (~ arr_nan).sum(axis=0)

        median = np.nanmedian(arr, axis=0)
        mc = np.r_[tuple(_calc_mc(arr[:, i], median[i]) for i in range(median.shape[0]))]
        Q1 = np.nanpercentile(arr, 25, axis=0)
        Q3 = np.nanpercentile(arr, 75, axis=0)
        IQR = Q3 - Q1

        up_bound = np.where(mc >= 0, Q3 + 1.5 * np.exp(3 * mc) * IQR, Q3 + 1.5 * np.exp(4 * mc) * IQR)
        down_bound = np.where(mc >= 0, Q1 - 1.5 * np.exp(-4 * mc) * IQR, Q1 - 1.5 * np.exp(-3 * mc) * IQR)

        Q99 = np.nanpercentile(arr, (1 - alpha) * 100, axis=0)
        Q01 = np.nanpercentile(arr, alpha * 100, axis=0)
        up_bound = np.where(up_bound > Q99, up_bound, Q99)
        down_bound = np.where(down_bound < Q01, down_bound, Q01)

        up_mask = (arr <= up_bound) | arr_nan
        down_mask = (arr >= down_bound) | arr_nan
        arr_up = np.ma.array(arr, mask=up_mask, fill_value=np.nan)
        arr_down = np.ma.array(arr, mask=down_mask, fill_value=np.nan)
        up_count = arr_up.count(axis=0)
        down_count = arr_down.count(axis=0)
        if out == 'pct':
            return np.r_['0,2', up_count / arr_count, down_count / arr_count]

        elif out == 'raw_rank':
            mad = np.nanmedian(np.abs(arr - median), axis=0)
            arr[~ up_mask] = (up_bound + 0.1483 * mad * bottleneck.nanrankdata(
                arr_up.filled(), axis=0) / up_count)[~ up_mask]
            arr[~ down_mask] = (down_bound - 0.1483 * mad * (1 + (1 - bottleneck.nanrankdata(
                arr_down.filled(), axis=0)) / down_count))[~ down_mask]

        elif out == 'raw':
            arr[~ up_mask] = up_bound.repeat(arr.shape[0]).reshape(arr.T.shape).T[~ up_mask]
            arr[~ down_mask] = down_bound.repeat(arr.shape[0]).reshape(arr.T.shape).T[~ down_mask]

        elif out == 'short':
            arr[~ up_mask] = np.nan
            arr[~ down_mask] = np.nan
        else:
            raise ValueError("param out must be pct, raw or short.")
        arr = arr.swapaxes(0, axis)
        return arr

    elif method == 'pct':
        arr = arr.swapaxes(0, axis).astype(float)
        arr_nan = np.isnan(arr)
        arr_count = (~ arr_nan).sum(axis=0)

        Q99 = np.nanpercentile(arr, (1 - alpha) * 100, axis=0)
        Q01 = np.nanpercentile(arr, alpha * 100, axis=0)

        up_mask = (arr <= Q99) | arr_nan
        down_mask = (arr >= Q01) | arr_nan
        arr_up = np.ma.array(arr, mask=up_mask, fill_value=np.nan)
        arr_down = np.ma.array(arr, mask=down_mask, fill_value=np.nan)
        up_count = arr_up.count(axis=0)
        down_count = arr_down.count(axis=0)
        if out == 'pct':
            return np.r_['0,2', up_count / arr_count, down_count / arr_count]

        elif out == 'raw_rank':
            median = np.nanmedian(arr, axis=0)
            mad = np.nanmedian(np.abs(arr - median), axis=0)
            arr[~ up_mask] = (Q99 + 0.1483 * mad * bottleneck.nanrankdata(
                arr_up.filled(), axis=0) / up_count)[~ up_mask]
            arr[~ down_mask] = (Q01 - 0.1483 * mad * (1 + (1 - bottleneck.nanrankdata(
                arr_down.filled(), axis=0)) / down_count))[~ down_mask]

        elif out == 'raw':
            arr[~ up_mask] = Q99.repeat(arr.shape[0]).reshape(arr.T.shape).T[~ up_mask]
            arr[~ down_mask] = Q01.repeat(arr.shape[0]).reshape(arr.T.shape).T[~ down_mask]

        elif out == 'short':
            arr[~ up_mask] = np.nan
            arr[~ down_mask] = np.nan
        else:
            raise ValueError("param out must be pct, raw or short.")
        arr = arr.swapaxes(0, axis)
        return arr

    else:
        raise ValueError("method must be mad, mv, box or pct.")

def box_cox_transform(arr):

    container = np.full_like(arr, np.nan)
    select = np.isfinite(arr)
    for i in range(arr.shape[0]):
        container[i, select[i]] = boxcox(arr[i, select[i]])[0]
    return container

def standardize(arr, axis=-1, method='mv'):

    if method == 'mad':
        arr = arr.swapaxes(0, axis).astype(float)
        median = np.nanmedian(arr, axis=0)
        mad = np.nanmedian(np.abs(arr - median), axis=0)
        arr -= median
        arr /= mad * 1.483
        arr = arr.swapaxes(0, axis)
        return arr

    elif method == 'mv':
        arr = arr.swapaxes(0, axis).astype(float)
        mean = np.nanmean(arr, axis=0)
        std = np.nanstd(arr, ddof=1, axis=0)
        arr -= mean
        arr /= std
        arr = arr.swapaxes(0, axis)
        return arr

    elif method == 'uniform':
        arr = arr.swapaxes(0, axis).astype(float)
        arr = bottleneck.nanrankdata(arr, axis=0)
        arr -= 1
        arr /= np.nanmax(arr, axis=0)
        arr -= 0.5
        arr /= np.nanstd(arr, ddof=1, axis=0)
        arr = arr.swapaxes(0, axis)
        return arr

    elif method == 'normal':
        arr = arr.swapaxes(0, axis).astype(float)
        arr = bottleneck.nanrankdata(arr, axis=0)
        arr -= 1
        arr /= np.nanmax(arr, axis=0)
        arr *= 0.9974
        arr += 0.0013
        arr = norm.ppf(arr)
        arr = arr.swapaxes(0, axis)
        return arr

    elif method == 'boxcox':
        assert arr.ndim == 2
        arr = arr.swapaxes(0, axis).astype(float)
        arr_min = np.nanmin(arr, axis=0)
        arr -= arr_min - 1
        arr = arr.swapaxes(0, -1)
        arr = box_cox_transform(arr)
        arr = arr.swapaxes(0, -1)
        mean = np.nanmean(arr, axis=0)
        std = np.nanstd(arr, ddof=1, axis=0)
        arr -= mean
        arr /= std
        arr = arr.swapaxes(0, axis)
        return arr

    else:
        raise ValueError("method must be mad, mv, uniform or normal.")

def ols_X(X, out='residual', n_axis=-1):

    X = X.swapaxes(0, n_axis)
    miss = np.any(np.isnan(X), axis=1)
    X[miss] = 0
    if out == 'residual':
        Y = np.eye(X.shape[0]) - X @ np.linalg.inv(X.T @ X) @ X.T
    elif out == 'beta':
        Y = np.linalg.inv(X.T @ X) @ X.T
    else:
        raise ValueError("It is too hard for me to calculate.")
    return Y, miss

def neutralize(arr, date, code_list, stock_pool_day, ind_type='SW', method='ols', fill='mad', axis=-1):

    if ind_type == 'SW':
        ind = get_daily_1day(['SW1', 'SW2'], date, code_list).T.values
        ind[0][ind[0] == 6134] = ind[1][ind[0] == 6134]
        ind = ind[0]
        ind_codes = np.unique(ind)
        ind_codes = list(ind_codes[np.isfinite(ind_codes)])
    elif ind_type == 'CITICS':
        ind = get_daily_1day(['CITICS1', 'CITICS2'], date, code_list).T.values
        ind[0][ind[0] == 'b10m'] = ind[1][ind[0] == 'b10m']
        ind = ind[0]
        ind_codes = sorted(list(set(ind) - {np.nan}))
    elif isinstance(ind_type, pd.DataFrame):
        ind = ind_type.loc[date].reindex(code_list).values
        if ind.dtype is 'float':
            ind_codes = np.unique(ind)
            ind_codes = list(ind_codes[np.isfinite(ind_codes)])
        else:
            ind_codes = sorted(list(set(ind) - {np.nan}))
    else:
        raise TypeError("ind_type must be SW, CITICS or pandas.DataFrame object")

    ind = np.r_['0,2', tuple(ind == x for x in ind_codes)]
    mv = np.log(get_daily_1day(['mkt_cap_ard'], date, code_list).T.values[0])

    arr = standardize(arr.swapaxes(-1, axis).copy())


    if method == 'ols':
        mv_ind = np.r_['0,2', mv, ind].copy()
        X, miss = ols_X(mv_ind, out='residual', n_axis=-1)
        mask = np.isnan(arr) | miss
        arr[mask] = 0
        arr = arr @ X
        arr[mask] = np.nan

    elif method in ('mad', 'mv', 'uniform', 'normal'):
        for i in range(ind.shape[0]):
            temp = standardize(np.ma.array(arr, mask=~ind[i].repeat(arr.shape[0]).reshape(arr.T.shape).T,
                                           fill_value=np.nan).filled(), axis=-1, method=method)
            temp_mv = standardize(np.ma.array(mv, mask=~ind[i], fill_value=np.nan).filled(), axis=-1, method=method)
            arr[:, ind[i]] = temp[:, ind[i]]
            mv[ind[i]] = temp_mv[ind[i]]

        X, miss = ols_X(mv[None, :], out='residual', n_axis=-1)
        mask = np.isnan(arr) | miss
        arr[mask] = 0
        arr = arr @ X
        arr[mask] = np.nan

    elif method is not None:
        raise ValueError("neutralize method must be ols, mad, mv, uniform, normal or None")


    if fill == 'ind_mad':
        for i in range(ind.shape[0]):
            arr[ind[i] & ~ np.isfinite(arr) & stock_pool_day] = np.nanmedian(arr[:, ind[i]], axis=1).repeat(
                arr.shape[1]).reshape(arr.shape)[ind[i] & ~ np.isfinite(arr) & stock_pool_day]
        arr[stock_pool_day & ~ np.isfinite(arr)] = 0

    elif fill == 'ind_mean':
        for i in range(ind.shape[0]):
            arr[ind[i] & ~ np.isfinite(arr) & stock_pool_day] = np.nanmean(arr[:, ind[i]], axis=1).repeat(
                arr.shape[1]).reshape(arr.shape)[ind[i] & ~ np.isfinite(arr) & stock_pool_day]
        arr[stock_pool_day & ~ np.isfinite(arr)] = 0

    elif fill == 'mean':
        arr[stock_pool_day & ~ np.isfinite(arr)] = 0

    elif fill is not None:
        raise ValueError("fill method must be ind_mad, ind_mean, mean or None")


    return arr

def corrcoef(X, y, axis=-1):

    X = X.swapaxes(0, axis)
    X[~ np.isfinite(y)] = np.nan

    X = X - np.nanmean(X, axis=0)
    y = y - np.nanmean(y)
    multi = np.nanmean(X.T * y, axis=1) / (np.nanstd(X, axis=0) * np.nanstd(y))
    multi[np.isinf(multi)] = np.nan
    return multi

class AlphaDataPrepare(object):


    def __init__(self, start_date, end_date, middle_address):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        date_num = len(date_list)

        self.middle_address = middle_address
        self.start_date = start_date
        self.end_date = end_date
        self.date_list = date_list
        self.date_num = date_num

    def set_stock_pool(self, stock_list='ALL', no_ST=True, least_live_days=240, no_pause=True, least_recover_days=1,
                       no_pause_limit=0.5, no_pause_stats_days=120, no_limit_up=False, no_limit_down=False,
                       other_limit=None, stock_pool_address=None):

        stock_pool = clean_stock_list(stock_list=stock_list, no_ST=no_ST, least_live_days=least_live_days,
                                      no_pause=no_pause, least_recover_days=least_recover_days,
                                      no_pause_limit=no_pause_limit, no_pause_stats_days=no_pause_stats_days,
                                      no_limit_up=no_limit_up, no_limit_down=no_limit_down,
                                      other_limit=other_limit, start_date=self.start_date, end_date=self.end_date)

        stock_pool_address = self.middle_address if stock_pool_address is None else stock_pool_address
        stock_pool.to_hdf('%s/stock_pool.h5' % stock_pool_address, 'stock_pool', format='t')

        code_list = stock_pool.columns.to_list()
        code_num = len(code_list)

        stock_pool = stock_pool.values
        code_valid_num = stock_pool.sum(axis=1)

        self.stock_pool = stock_pool
        self.code_list = code_list
        self.code_num = code_num
        self.code_valid_num = code_valid_num

    def load_stock_pool(self, stock_pool_address=None):

        stock_pool_address = self.middle_address if stock_pool_address is None else stock_pool_address
        stock_pool = get_daily_1factor('stock_pool', date_list=self.date_list, diy_address=stock_pool_address)
        code_list = stock_pool.columns.to_list()
        code_num = len(code_list)
        stock_pool = stock_pool.values
        code_valid_num = stock_pool.sum(axis=1)

        self.stock_pool = stock_pool
        self.code_list = code_list
        self.code_num = code_num
        self.code_valid_num = code_valid_num

    def set_future(self, future_days=5, price_type='twap', future_address=None):

        if isinstance(future_days, int):
            future_days = list(range(1, future_days + 1))
        elif not isinstance(future_days, list):
            raise TypeError('future_days must be int or list')
        future_days_max = max(future_days)
        future_date_num = len(future_days)

        price_raw_dates = get_date_range(get_pre_trade_date(self.start_date, -1),
                                         get_pre_trade_date(self.end_date, - future_days_max - 1))
        price = get_daily_1factor(price_type, price_raw_dates, self.code_list) * get_daily_1factor(
            'adjfactor', price_raw_dates, self.code_list)
        future = np.concatenate(tuple(np.atleast_3d(price.pct_change(x).shift(-x).values) for x in future_days),
                                axis=2).transpose(2, 0, 1)[:, :-future_days_max]
        future[np.arange(future_date_num)[:, None, None], ~ self.stock_pool] = np.nan

        future_address = self.middle_address if future_address is None else future_address
        np.save('%s/future_days' % future_address, np.asanyarray(future_days))
        np.save('%s/future' % future_address, future)

        self.future_days = future_days
        self.future_days_max = future_days_max
        self.future_date_num = future_date_num
        self.future = future

    def load_future(self, future_address=None):

        future_address = self.middle_address if future_address is None else future_address
        future_days = list(np.load('%s%s.npy' % (future_address, 'future_days')))
        future = np.load('%s%s.npy' % (future_address, 'future'))

        future_days_max = max(future_days)
        future_date_num = len(future_days)

        self.future_days = future_days
        self.future_days_max = future_days_max
        self.future_date_num = future_date_num
        self.future = future

    def get_future_standardize(self, method, future_standardize_address=None):

        future_standardize = standardize(self.future, method=method)
        future_standardize_address = (self.middle_address if future_standardize_address is None
                                      else future_standardize_address)
        np.save('%s/future_%s' % (future_standardize_address, method), future_standardize)

    def set_factor_list(self, factor_list=None, factor_list_address=None,
                        factor_address='/data/user/015518/quant_data/qualified_factor/x_day_lib/20181231/'):

        if factor_list is None and factor_address is None:
            raise ValueError("either factor_list or factor_address must be passed")
        elif factor_list is None:
            factor_list = pd.read_parquet('%s/mddate=%s' % (factor_address, self.end_date)).set_index(
                'stock').columns.to_list()
            factor_list = sorted([x for x in factor_list if re.match('^Fix1[0134][03]0_', x) is None])
        else:
            factor_list = sorted(factor_list)

        factor_list_address = self.middle_address if factor_list_address is None else factor_list_address
        np.save('%s/factor_list' % factor_list_address, np.asanyarray(factor_list))
        factor_num = len(factor_list)

        self.factor_list = factor_list
        self.factor_num = factor_num

    def load_factor_list(self, factor_list_address=None):

        factor_list_address = self.middle_address if factor_list_address is None else factor_list_address
        factor_list = list(np.load('%s%s.npy' % (factor_list_address, 'factor_list')))
        factor_num = len(factor_list)

        self.factor_list = factor_list
        self.factor_num = factor_num

    def get_day_factor_base(self, date, factor_complete_limit=0.8, factor_diversity_limit=0.75, corr=True,
                            corr_address=None, factor_pool_address=None,
                            factor_address='/data/user/015518/quant_data/qualified_factor/x_day_lib/20181231/'):

        day = self.date_list.index(date)
        stock_pool = self.stock_pool[day]
        code_valid_num = self.code_valid_num[day]

        factor = load_factor(date, factor_address, self.factor_list, self.code_list)

        if corr:
            factor_corr = factor.T.corr().values
            corr_address = self.middle_address if corr_address is None else corr_address
            np.save(corr_address + 'factor_corr ' + str(date), factor_corr)
            self._factor_corr = factor_corr

        factor = factor.values
        factor[np.isinf(factor) | ~ stock_pool] = np.nan

        factor_complete = np.ma.masked_invalid(factor).count(axis=1) / code_valid_num
        factor_diversity = np.r_[tuple(np.unique(np.ma.masked_invalid(factor[x])).count()
                                       for x in range(factor.shape[0]))] / code_valid_num

        factor_pool = (factor_complete > factor_complete_limit) & (factor_diversity > factor_diversity_limit)

        factor_pool_address = self.middle_address if factor_pool_address is None else factor_pool_address
        np.save(factor_pool_address + 'factor_pool ' + str(date), factor_pool)
        np.save(factor_pool_address + 'factor ' + str(date), factor)

        self._day = day
        self._date = date
        self._factor = factor
        self._stock_pool = stock_pool
        self._factor_pool = factor_pool

    def get_day_factor_winsorize(self, winsorize_method='mad', winsorize_alpha=0.01, date=None,
                                 factor_pool_address=None, factor_winsorize_address=None):

        factor_pool_address = self.middle_address if factor_pool_address is None else factor_pool_address
        factor = (np.load(factor_pool_address + 'factor ' + str(date) + '.npy') if date is not None else self._factor)
        date = date if date is not None else self._date

        if winsorize_method is None:
            factor_winsorize = factor
        else:
            factor_winsorize = winsorize(factor, method=winsorize_method, alpha=winsorize_alpha)

        factor_winsorize_address = self.middle_address if factor_winsorize_address is None else factor_winsorize_address
        np.save(factor_winsorize_address + 'factor_winsorize ' + str(date), factor_winsorize)

        self._factor_winsorize = factor_winsorize
        self._date = date

    def get_day_factor_neutralize(self, neutralize_ind='SW', neutralize_method='ols', neutralize_fill='ind_mad',
                                  date=None, factor_winsorize_address=None, factor_neutral_address=None):

        factor_winsorize_address = self.middle_address if factor_winsorize_address is None else factor_winsorize_address
        factor_winsorize = (np.load(factor_winsorize_address + 'factor_winsorize ' + str(date) + '.npy')
                            if date is not None else self._factor_winsorize)
        stock_pool = self.stock_pool[self.date_list.index(date)] if date is not None else self.stock_pool[self._day]
        date = date if date is not None else self._date

        factor_neutral = neutralize(factor_winsorize, date, self.code_list, stock_pool,
                                    ind_type=neutralize_ind, method=neutralize_method, fill=neutralize_fill)

        factor_neutral_address = self.middle_address if factor_neutral_address is None else factor_neutral_address
        np.save(factor_neutral_address + 'factor_neutral ' + str(date), factor_neutral)

        self._factor_neutral = factor_neutral
        self._stock_pool = stock_pool
        self._date = date

    def get_day_factor_standardize(self, standardize_method='mv', date=None,
                                   factor_neutral_address=None, factor_standardize_address=None):

        factor_neutral_address = self.middle_address if factor_neutral_address is None else factor_neutral_address
        factor_neutral = (np.load(factor_neutral_address + 'factor_neutral ' + str(date) + '.npy')
                            if date is not None else self._factor_neutral)
        date = date if date is not None else self._date

        factor_standardize = standardize(factor_neutral, method=standardize_method)

        factor_standardize_address = (self.middle_address if factor_standardize_address
                                                             is None else factor_standardize_address)
        np.save(factor_standardize_address + 'factor_standardize ' + str(date), factor_standardize)

        self._factor_standardize = factor_standardize
        self._date = date

    def get_day_future(self, date=None):

        day = self.date_list.index(date) if date is not None else self.date_list.index(self._date)
        future = self.future[:, day, :]
        return future

    def get_day_middle_factor(self, factor_type='standardize', date=None, factor_address=None):

        if date is None:
            if factor_type == 'raw':
                factor = self._factor
            elif factor_type == 'winsorize':
                factor = self._factor_winsorize
            elif factor_type == 'neutral':
                factor = self._factor_neutral
            elif factor_type == 'standardize':
                factor = self._factor_standardize
            else:
                raise ValueError("factor_type must be raw, winsorize, neutral or standardize")
        else:
            factor_address = self.middle_address if factor_address is None else factor_address
            if factor_type == 'raw':
                factor = np.load(factor_address + 'factor ' + str(date) + '.npy')
            elif factor_type == 'winsorize':
                factor = np.load(factor_address + 'factor_winsorize ' + str(date) + '.npy')
            elif factor_type == 'neutral':
                factor = np.load(factor_address + 'factor_neutral ' + str(date) + '.npy')
            elif factor_type == 'standardize':
                factor = np.load(factor_address + 'factor_standardize ' + str(date) + '.npy')
            else:
                raise ValueError("factor_type must be raw, winsorize, neutral or standardize")
        return factor

    def calc_day_IC(self, factor_type='standardize', date=None, factor_address=None, IC_address=None):

        factor = self.get_day_middle_factor(factor_type, date, factor_address)
        future = self.get_day_future(date)
        date = date if date is not None else self._date

        IC = np.r_['0,2', tuple(corrcoef(factor, future[x]) for x in range(self.future_date_num))]

        IC_address = self.middle_address if IC_address is None else IC_address
        np.save(IC_address + 'IC ' + str(date), IC)

        self._IC = IC
        self._date = date

    def calc_day_MI(self, factor_type='standardize', date=None,
                    factor_address=None, factor_pool_address=None, MI_address=None):

        factor = self.get_day_middle_factor(factor_type, date, factor_address)
        future = self.get_day_future(date)
        date = date if date is not None else self._date

        factor_pool_address = self.middle_address if factor_pool_address is None else factor_pool_address
        factor_pool = (np.load(factor_pool_address + 'factor_pool ' + str(date) + '.npy') if date is not None
                       else self._factor_pool)

        MI = np.zeros((factor.shape[0], future.shape[0]))
        MI[factor_pool] = np.r_['0,2', tuple(mutual_info_regression(factor[factor_pool][:, np.isfinite(
            future[x])].T, future[x][np.isfinite(future[x])]) for x in range(self.future_date_num))].T
        MI = MI.T

        MI_address = self.middle_address if MI_address is None else MI_address
        np.save(MI_address + 'MI ' + str(date), MI)

        self._MI = MI
        self._date = date

    def get_day_rank(self, factor_type='standardize', date=None, factor_address=None):

        factor = self.get_day_middle_factor(factor_type, date, factor_address)
        future = self.get_day_future(date)
        date = date if date is not None else self._date
        code_valid_num = self.code_valid_num[self.date_list.index(date)]

        factor_rank = bottleneck.nanrankdata(factor, axis=1) / code_valid_num
        future_rank = bottleneck.nanrankdata(future, axis=1) / code_valid_num

        self._factor_rank = factor_rank
        self._future_rank = future_rank
        self._rank_future = future
        self._rank_factor = factor
        self._rank_date = date

    def calc_day_rank_IC(self, rank_IC_address=None):

        rank_IC = np.r_['0,2', tuple(corrcoef(self._factor_rank, self._future_rank[x]) for x in
                                     range(self.future_date_num))]

        rank_IC_address = self.middle_address if rank_IC_address is None else rank_IC_address
        np.save(rank_IC_address + 'rank_IC ' + str(self._rank_date), rank_IC)
        self._rank_IC = rank_IC

    def get_day_group(self, groups=10, factor_group_address=None):

        factor_group = np.ceil(self._factor_rank * groups)
        future_group = np.ceil(self._future_rank * groups)

        factor_group_address = self.middle_address if factor_group_address is None else factor_group_address
        np.save(factor_group_address + 'factor_group ' + str(self._rank_date), factor_group)

        self._factor_group = factor_group
        self._future_group = future_group
        self.groups = groups

    def calc_day_group_MI(self, factor_pool_address=None, group_MI_address=None):

        factor_pool_address = self.middle_address if factor_pool_address is None else factor_pool_address
        factor_pool = (np.load(factor_pool_address + 'factor_pool ' + str(self._rank_date) + '.npy')
                       if (self._rank_date != self._date) | (not hasattr(self, '_factor_pool')) else self._factor_pool)

        group_MI = np.zeros((self._rank_factor.shape[0], self._future_group.shape[0]))
        group_MI[factor_pool] = np.r_['0,2', tuple(mutual_info_classif(self._rank_factor[factor_pool][:, np.isfinite(
            self._future_group[x])].T, self._future_group[x][np.isfinite(self._future_group[x])]) for x in range(
            self.future_date_num))].T
        group_MI = group_MI.T

        group_MI_address = self.middle_address if group_MI_address is None else group_MI_address
        np.save(group_MI_address + 'group_MI ' + str(self._rank_date), group_MI)
        self._group_MI = group_MI

    def calc_day_group_active(self, group_active_address=None):

        future_repeat = self._rank_future[:, None, :].repeat(self._factor_group.shape[0], axis=1)

        group_active = np.c_['0,3', tuple(np.ma.array(future_repeat, mask=np.isnan(future_repeat) | (
                self._factor_group != x)).mean(axis=2).data for x in range(1, self.groups + 1))].transpose(2, 0, 1)
        group_active -= np.nanmean(self._rank_future, axis=1)
        group_active = group_active.transpose(0, 2, 1)

        group_active_address = self.middle_address if group_active_address is None else group_active_address
        np.save(group_active_address + 'group_active ' + str(self._rank_date), group_active)
        self._group_active = group_active

    def calc_day_group_IC(self, date=None, group_active_address=None, group_IC_address=None):

        group_active_address = self.middle_address if group_active_address is None else group_active_address
        group_active = (np.load(group_active_address + 'group_active ' + str(date) + '.npy')
                        if date is not None else self._group_active)
        date = date if date is not None else self._date
        groups = group_active.shape[2]

        group_IC = (np.nanmean((bottleneck.nanrankdata(group_active, axis=2) - (groups + 1) / 2) * (np.arange(
            1, groups + 1) - (groups + 1) / 2), axis=2) / np.nanstd(bottleneck.nanrankdata(
            group_active, axis=2), axis=2) / np.nanstd(np.arange(1, groups + 1))).T

        group_IC_address = self.middle_address if group_IC_address is None else group_IC_address
        np.save(group_IC_address + 'group_IC ' + str(date), group_IC)
        self._group_IC = group_IC

    def calc_factor_turn(self, future_days=None, factor_pool_address=None,
                         factor_group_address=None, factor_turn_address=None):

        factor_pool_address = self.middle_address if factor_pool_address is None else factor_pool_address
        factor_group_address = self.middle_address if factor_group_address is None else factor_group_address
        factor_turn_address = self.middle_address if factor_turn_address is None else factor_turn_address

        if future_days is None:
            future_days = self.future_days
        elif isinstance(future_days, int):
            future_days = list(range(1, future_days + 1))
        elif not isinstance(future_days, list):
            raise TypeError('future_days must be int or list')

        factor_pool = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (factor_pool_address, 'factor_pool', date))
                                         for date in self.date_list)]

        factor_group = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (factor_group_address, 'factor_group', date))
                                         for date in self.date_list)]

        group_head = factor_group == np.nanmax(factor_group[0])
        group_tail = factor_group == 1

        turn_head = tuple((group_head[future_days[x]:] != group_head[:-future_days[x]]).sum(axis=2) /
                          (group_head[future_days[x]:].sum(axis=2) + group_head[:-future_days[x]].sum(axis=2)) /
                          future_days[x] for x in range(len(future_days)))
        for x in range(len(future_days)):
            turn_head[x][~(factor_pool[future_days[x]:] & factor_pool[:-future_days[x]])] = np.nan
        turn_head = tuple(np.pad(turn_head[x], ((future_days[x], 0), (0, 0)), mode='mean',
                                 stat_length=((future_days[x], 0), (0, 0))) for x in range(len(future_days)))
        turn_head = np.r_['0,3', turn_head]

        turn_tail = tuple((group_tail[future_days[x]:] != group_tail[:-future_days[x]]).sum(axis=2) /
                          (group_tail[future_days[x]:].sum(axis=2) + group_tail[:-future_days[x]].sum(axis=2)) /
                          future_days[x] for x in range(len(future_days)))
        for x in range(len(future_days)):
            turn_tail[x][~(factor_pool[future_days[x]:] & factor_pool[:-future_days[x]])] = np.nan
        turn_tail = tuple(np.pad(turn_tail[x], ((future_days[x], 0), (0, 0)), mode='mean',
                                 stat_length=((future_days[x], 0), (0, 0))) for x in range(len(future_days)))
        turn_tail = np.r_['0,3', turn_tail]

        _factor_turn = np.r_['0,4', turn_tail, turn_head].transpose(2, 0, 1, 3)

        np.save(factor_turn_address + '_factor_turn', _factor_turn)

if __name__ == '__main__':

    middle_address = '/data/user/015836/model/temp20200527/'

    start_date = 20140102
    end_date = 20181228

    price_type = 'twap'
    future_days = 5

    factor_complete_limit = 0.8
    factor_diversity_limit = 0.75

    #mad, mv, box, pct
    winsorize_method, winsorize_alpha = 'mad', 0.01
    #'SW', 'CITICS'
    neutralize_ind = 'SW'
    #None, ols, mad, mv, uniform, norm
    neutralize_method = 'ols'
    #None, mad, mean
    neutralize_fill = 'ind_mad'
    #mv, mad, norm, uniform
    standardize_method = 'boxcox'

    future_standardize_method = 'mv'

    groups = 10

    other_limit = {'mkt_cap_ard': 0.05}

    adp = AlphaDataPrepare(start_date, end_date, middle_address)
    #adp.set_stock_pool(other_limit=other_limit)
    #adp.set_future(future_days=future_days, price_type=price_type)
    #adp.set_factor_list()
    #adp.get_future_standardize(future_standardize_method)

    adp.load_stock_pool()
    adp.load_future()
    adp.load_factor_list()

    def data_prepare(date_list, line=0):

        for date in tqdm(date_list, desc=str(line)):
            #adp.get_day_factor_base(date, factor_complete_limit, factor_diversity_limit)
            #adp.get_day_factor_winsorize(winsorize_method, winsorize_alpha)
            #adp.get_day_factor_neutralize(neutralize_ind, neutralize_method, neutralize_fill)
            adp.get_day_factor_standardize(standardize_method, date=date,
                                           factor_standardize_address='/data/user/015836/model/temp20200609/')
            #adp.calc_day_IC(date=date)
            #adp.get_day_rank(date=date)
            #adp.calc_day_rank_IC()
            #adp.get_day_group(groups=groups)
            #adp.calc_day_group_active()
            #adp.calc_day_group_IC(date=date)

    multiprocess(20, data_prepare, adp.date_list)

    import time
    t = time.time()
    adp.calc_factor_turn(future_days)
    time.time() - t

    def data_prepare_MI(date_list, line=0):

        for date in tqdm(date_list, desc=str(line)):
            adp.calc_day_MI(date=date)
            adp.get_day_rank(date=date)
            adp.get_day_group()
            adp.calc_day_group_MI()

    multiprocess(20, data_prepare_MI, adp.date_list)

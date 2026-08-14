import os
import bottleneck
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.stats import norm
from multiprocessing import Pool
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.stockList import trans_windcode2int, clean_stock_list
from dataApi.getData import get_daily_1day, get_daily_1factor

def winsorize(arr, axis=-1, method='mad', out='raw', alpha=0.01):

    if method == 'mad':
        arr = arr.swapaxes(0, axis).astype(float)
        median = np.nanmedian(arr, axis=0)
        mad = np.nanmedian(np.abs(arr - median), axis=0)
        arr_nan = np.isnan(arr)
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

        if fill == 'mad':
            for i in range(ind.shape[0]):
                arr[ind[i] & ~ np.isfinite(arr) & stock_pool_day] = np.nanmedian(arr[:, ind[i]], axis=1).repeat(
                    arr.shape[1]).reshape(arr.shape)[ind[i] & ~ np.isfinite(arr) & stock_pool_day]
        elif fill == 'mean':
            for i in range(ind.shape[0]):
                arr[ind[i] & ~ np.isfinite(arr) & stock_pool_day] = np.nanmean(arr[:, ind[i]], axis=1).repeat(
                    arr.shape[1]).reshape(arr.shape)[ind[i] & ~ np.isfinite(arr) & stock_pool_day]

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

    else:
        if fill == 'mad':
            for i in range(ind.shape[0]):
                arr[ind[i] & ~ np.isfinite(arr) & stock_pool_day] = np.nanmedian(arr[:, ind[i]], axis=1).repeat(
                    arr.shape[1]).reshape(arr.shape)[ind[i] & ~ np.isfinite(arr) & stock_pool_day]
        elif fill == 'mean':
            for i in range(ind.shape[0]):
                arr[ind[i] & ~ np.isfinite(arr) & stock_pool_day] = np.nanmean(arr[:, ind[i]], axis=1).repeat(
                    arr.shape[1]).reshape(arr.shape)[ind[i] & ~ np.isfinite(arr) & stock_pool_day]

    arr[stock_pool_day & ~ np.isfinite(arr)] = 0

    return arr

def load_factor(date, factor_list, factor_address, code_list=None):

    file_name = os.listdir('%s/mddate=%s' % (factor_address, date))[0]
    df = pd.read_parquet('%s/mddate=%s/%s' % (factor_address, date, file_name), columns=['stock'] + factor_list)
    df.set_index('stock', inplace=True)
    df.index = df.index.map(trans_windcode2int)
    if code_list is not None:
        return df.reindex(code_list).T
    else:
        return df.T

def load_future(stock_pool, future_days, start_date, end_date, code_list, price_type):

    if isinstance(future_days, int):
        future_days = list(range(1, future_days + 1))
    elif not isinstance(future_days, list):
        raise TypeError('future_days must be int or list')
    future_days_max = max(future_days)
    future_date_num = len(future_days)
    price_raw_dates = get_date_range(get_pre_trade_date(start_date, -1),
                                     get_pre_trade_date(end_date, -future_days_max - 1))
    price = get_daily_1factor(price_type, price_raw_dates, code_list) * get_daily_1factor(
        'adjfactor', price_raw_dates, code_list)
    future = np.concatenate(tuple(np.atleast_3d(price.pct_change(x).shift(-x).values) for x in future_days),
                            axis=2).transpose(2, 0, 1)[:, :-future_days_max]
    future[np.arange(future_date_num)[:, None, None], ~stock_pool] = np.nan
    return future

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

def corrcoef(X, y, axis=-1):

    X = X.swapaxes(0, axis)
    X[~ np.isfinite(y)] = np.nan

    X = X - np.nanmean(X, axis=0)
    y = y - np.nanmean(y)
    multi = np.nanmean(X.T * y, axis=1) / (np.nanstd(X, axis=0) * np.nanstd(y))
    multi[np.isinf(multi)] = np.nan
    return multi

def _preprocess_factor(sub_list, date_list, code_list, factor_list, factor_address, stock_pool, code_valid_num, future,
                       factor_complete_limit, factor_diversity_limit, winsorize_method, winsorize_alpha, neutralize_ind,
                       neutralize_method, neutralize_fill, standardize_method, groups, line):

    for date in tqdm(sub_list, desc=str(line)):

        day = date_list.index(date)
        stock_pool_day = stock_pool[day]
        code_valid_num_day = code_valid_num[day]
        future_day = future[:, day, :]

        factor = load_factor(date, factor_list, factor_address, code_list)
        factor_corr = factor.T.corr().values
        factor = factor.values
        factor[np.isinf(factor) | ~ stock_pool_day] = np.nan

        factor_complete = np.ma.masked_invalid(factor).count(axis=1) / code_valid_num_day
        factor_diversity = np.r_[tuple(np.unique(np.ma.masked_invalid(factor[x])).count()
                                       for x in range(factor.shape[0]))] / code_valid_num_day

        factor_pool = (factor_complete > factor_complete_limit) & (factor_diversity > factor_diversity_limit)
        factor = factor[factor_pool, :]

        factor_winsorize = winsorize(factor, method=winsorize_method, alpha=winsorize_alpha)
        factor_neutral = neutralize(factor_winsorize, date, code_list, stock_pool_day,
                                    ind_type=neutralize_ind, method=neutralize_method, fill=neutralize_fill)
        factor_standardize = standardize(factor_neutral, method=standardize_method)

        IC = np.r_['0,2', tuple(corrcoef(factor_standardize, future_day[x]) for x in range(future_day.shape[0]))].T
        MI = np.r_['0,2', tuple(mutual_info_regression(factor_standardize[:, np.isfinite(future_day[x])].T, future_day[
            x][np.isfinite(future_day[x])]) for x in range(future_day.shape[0]))].T

        factor_rank = bottleneck.nanrankdata(factor_standardize, axis=1) / code_valid_num_day
        future_rank = bottleneck.nanrankdata(future_day, axis=1) / code_valid_num_day

        rank_IC = np.r_['0,2', tuple(corrcoef(factor_rank, future_rank[x]) for x in range(future_day.shape[0]))].T

        factor_group = np.ceil(factor_rank * groups)
        future_group = np.ceil(future_rank * groups)

        future_day_repeat = future_day[:, None, :].repeat(factor_group.shape[0], axis=1)

        group_active = np.c_['0,3', tuple(np.ma.array(future_day_repeat, mask=np.isnan(future_day_repeat) | (
                factor_group != x)).mean(axis=2).data for x in range(1, groups + 1))].transpose(2, 0, 1)
        group_active -= np.nanmean(future_day, axis=1)
        group_active = group_active.transpose(0, 2, 1)

        group_IC = np.nanmean((bottleneck.nanrankdata(group_active, axis=2) - (groups + 1) / 2) * (
                np.arange(1, groups + 1) - (groups + 1) / 2), axis=2) / np.nanstd(bottleneck.nanrankdata(
            group_active, axis=2), axis=2) / np.nanstd(np.arange(1, groups + 1))

        group_MI = np.r_['0,2', tuple(mutual_info_classif(factor_standardize[:, np.isfinite(
            future_group[x])].T, future_group[x][np.isfinite(future_group[x])])
                                      for x in range(future_group.shape[0]))].T

        np.save(middle_address + 'factor_corr ' + str(date), factor_corr)
        np.save(middle_address + 'factor_complete ' + str(date), factor_complete)
        np.save(middle_address + 'factor_diversity ' + str(date), factor_diversity)
        np.save(middle_address + 'factor_pool ' + str(date), factor_pool)
        np.save(middle_address + 'factor_standardize ' + str(date), factor_standardize)
        np.save(middle_address + 'IC ' + str(date), IC)
        np.save(middle_address + 'MI ' + str(date), MI)
        np.save(middle_address + 'rank_IC ' + str(date), rank_IC)
        np.save(middle_address + 'factor_group ' + str(date), factor_group)
        np.save(middle_address + 'group_active ' + str(date), group_active)
        np.save(middle_address + 'group_IC ' + str(date), group_IC)
        np.save(middle_address + 'group_MI ' + str(date), group_MI)

def _calc_daily_turn(date_list, code_valid_num, groups, middle_address):

    for date in tqdm(date_list):

        factor_pool = np.load('%s%s %s.npy' % (middle_address, 'factor_pool', date))
        factor_group = np.load('%s%s %s.npy' % (middle_address, 'factor_group', date))
        code_valid_num_day = code_valid_num[date_list.index(date)]

        group = np.full((factor_pool.shape[0], factor_group.shape[1]), np.nan)
        group[factor_pool, :] = factor_group

        if date == date_list[0]:
            factor_turn = np.full((groups, group.shape[0]), np.nan)
        else:
            factor_turn = np.r_['0,2', tuple(np.abs((group == x) * 1. - (gl == x) * 1.).sum(axis=1)
                                             for x in range(1, groups + 1))]
            factor_turn /= (code_valid_num_day + vl) / 2
            factor_turn[:, ~ factor_pool | ~ pl] = np.nan

        gl = group
        pl = factor_pool
        vl = code_valid_num_day

        np.save(middle_address + 'factor_turn ' + str(date), factor_turn)

def factor_preprocess(factor_list, factor_address, middle_address, start_date, end_date, price_type, future_days,
                      factor_complete_limit, factor_diversity_limit, winsorize_method, winsorize_alpha, neutralize_ind,
                      neutralize_method, neutralize_fill, standardize_method, groups):

    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240, no_pause=True,
                                  least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120, no_limit_up=False, no_limit_down=False,
                                  other_limit={'mkt_cap_ard': 0.05}, start_date=start_date, end_date=end_date)

    date_list = stock_pool.index.to_list()
    code_list = stock_pool.columns.to_list()
    stock_pool = stock_pool.values

    if isinstance(future_days, int):
        future_days = list(range(1, future_days + 1))
    elif not isinstance(future_days, list):
        raise TypeError('future_days must be int or list')

    future = load_future(stock_pool, future_days, start_date, end_date, code_list, price_type)
    code_valid_num = stock_pool.sum(axis=1)

    multiprocess(20, _preprocess_factor, date_list, date_list, code_list, factor_list, factor_address, stock_pool,
                 code_valid_num, future, factor_complete_limit, factor_diversity_limit, winsorize_method,
                 winsorize_alpha, neutralize_ind, neutralize_method, neutralize_fill, standardize_method, groups)

    _calc_daily_turn(date_list, code_valid_num, groups, middle_address)

if __name__ == '__main__':

    factor_list = [
        'APB1m_Mean5d',
        'APB5d',
        'APB5m_Mean5d',
        'AbnAmtRet',
        'AbnormalVolRaiseMom20d',
        'AbsRet2Deal',
        'AgainstBeta',
        'Aktr',
        'AmPmDiff',
        'AmihudLast120min10d',
        'AmtDealReDiff5d',
        'AmtEhdReverse',
        'AmtPerDealRetCorr',
        'AmtPerTradeInOutflow5d',
        'AmtPerTradeReSkew20d',
        'AmtPerTradeWeightedReturn',
        'AmtPerTradeWeightedReturn5d',
        'AmtRatioEntropy',
        'AmtRet',
        'AmtRet20d',
        'AmtRet5d',
        'AmtSkew3Day',
        'AmtStdBias',
        'AmtStdMean60d',
        'AmtStd_Mean2Std_5',
        'AmtVolStdRankMean5d',
        'AtrRetCorr',
        'AvgClose2Vwap_Std_5',
        'BeforehandRetCut20',
        'BeforehandRetCut30',
        'BeforehandRetResidual30',
        'BigOrderNetInflowRate5d',
        'BigOrderReturn20d',
        'BigPlayersTurnover',
        'BigPlayersVwap',
        'BoolDW',
        'BuyAmtStd3Day',
        'C9_DIFF60',
        'CEMV_CS30_SR20',
        'CEMV_CS30_Skew40',
        'CEMV_Skew40',
        'CEMVsharpe',
        'CEMVstd',
        'CSTurnpureCorrRet',
        'CSTurnpureCorrRetSharp',
        'CancelRateStd20d',
        'CapVolume',
        'CapVolumeRR',
        'CloseCorrTurnR2',
        'CloseOpenVolumeCorr',
        'ClosePercent2Journey',
        'ClosePercentDeal5d_up',
        'ClosePercentRank10d_up',
        'ClosePercentRank5d',
        'ClosePercentSharpe5d',
        'ClosePercentSwing5d',
        'ClosePercentUp5d',
        'CloseVolatility5d',
        'CloseVwapRetKurt',
        'CorrCloseRankTurn20d',
        'CorrCloseTurn10d_max',
        'CorrCloseTurn5d_max',
        'CorrCloseVol_Std10',
        'CorrCloseVol_Std_5',
        'CorrCloseVolumeSharpe',
        'CorrDelVolumePriceSharpe5d',
        'CorrDownVolumeSharpe',
        'CorrPVTUpCloseSharpe20d',
        'CorrRetAmtPct_CS15',
        'CorrRetVol_Mean_5',
        'CorrTurnPrice10min5dSharpe',
        'CorrVolReturn5d',
        'CsResidualSkew',
        'CumretClseSlope_60',
        'CybzCorrClose',
        'DailyPrfLP_6',
        'DavisWin',
        'DealnumSharpe',
        'DebtToAsset_std_3y',
        'DeltaTurnSkew',
        'DivMulStaVol',
        'DownSpeed',
        'DownUpMeanRatio5d',
        'DownUpSumRatio5d',
        'DownVolRatioDiff30',
        'Downward_volatility_20days',
        'DuoKongMix',
        'DuoKongPV',
        'EBITDev',
        'EMVA',
        'EP_Hist2_120D',
        'EarningRevision90d_nis',
        'ExceedSwingCorAmt',
        'ExtremeTurnStd',
        'FM10_GMTTM',
        'FM10_GTGTTM',
        'FM10_PROTTM',
        'FM11_GPM',
        'FM11_PTGTTM',
        'FM11_QGM',
        'FM11_QOP',
        'FM11_QOPYOY',
        'FM11_QROE',
        'FM11_YOYOP',
        'FM11_YOYTR',
        'FM13_PTG',
        'FM15_EPS',
        'FM18_PTG',
        'FM20_PTG',
        'FM2_GMA',
        'FM2_GPM',
        'FM2_OTGR',
        'FM2_PTG',
        'FM2_YOYE',
        'FM2_YOYTR',
        'FM3_YOYOP',
        'FM5_OTE',
        'FM5_OTG',
        'FM5_PTG',
        'FM5_QG',
        'FM5_ROETTM',
        'FM5_YOYNP',
        'FM8_GPM',
        'FM8_OPYOY',
        'FM8_PTGTTM',
        'FM8_QOP',
        'FM9_GPM',
        'FM9_ROATTM',
        'FM9_YOYPRO',
        'FR10d_1001',
        'FR20d_1001',
        'FR20d_1130',
        'FR40d',
        'FR40d_1001',
        'FallTurnover',
        'ForecastBPPercent120d',
        'ForecastEPChange60d',
        'ForecastEPDelta20d',
        'ForecastEPGChange60d',
        'ForecastEPPercent120d',
        'ForecastPE',
        'ForecastPEGDelta20d',
        'ForecastPEGDelta5d',
        'ForecastPEGPercent120d',
        'ForecastPEGRoll',
        'ForecastPEGRollChange40d',
        'ForecastPERoll',
        'FreeturnRankUpDownRatio_CS30',
        'GPMarTTMStandardGrowth',
        'GTJA176',
        'GTJA179',
        'GTJA2TransRolling20',
        'GTJA2TransRolling5',
        'GTJA36',
        'GTJA54',
        'GTJA64',
        'GTJA74',
        'GTJA_007',
        'GTJA_026',
        'GTJA_032',
        'GTJA_042',
        'GTJA_062',
        'GTJA_064',
        'GTJA_083',
        'GrahamValue',
        'GrowthRefined',
        'HighCandleBottom',
        'HighCloseTurnSharpe',
        'HighCloseTurnSharpe20',
        'HighCloseTurnSharpe80',
        'HighCloseTurnSigma',
        'HighLowStdRatio_mean20d',
        'HighVolCorrMax',
        'HighVolCorrStd',
        'HighVolumeCorr10d',
        'IVR_000300_20',
        'IdeaReverser5d',
        'IlliqNeg60d',
        'IndRankinglistEffect',
        'IndustriesPBROE',
        'IndustryMidBeta',
        'IndustryNeutralizedTurnoverStd',
        'IndustryReverse',
        'IntradayAmountRatioDay',
        'InvSta',
        'KNN30',
        'LargeSmallVolumeVWAPRatio',
        'Last30MinsVwapCloseRatio5d',
        'LastTurn',
        'LiqCorr',
        'LiqRatioAS',
        'LiqRatioSA',
        'LiquidityPure20Part2',
        'LongVolGrowthSharpe60d',
        'LoserList_200',
        'LowCandleBottom',
        'LowRtnVolGrowthSharpe60d',
        'LowRtnVolSkew60d',
        'MarketHolder',
        'MarketHolderMu',
        'MarketHolderSigma',
        'MarketTaker',
        'MarketTakerMu',
        'MarketTakerSigma',
        'MeanTurn2RetDown5d',
        'MedianDownAmtRatio',
        'MedianDownVarRatio',
        'MildMoneyMaker',
        'Min10VolBurst5Wegihted5d',
        'Min10mRetUpVar',
        'Min30CEMVbias',
        'Min30HW',
        'Min30TDis',
        'Min5LastHourMFI5d',
        'Min5VwapToClose20d',
        'Min60_RVstd',
        'MinARC2VRCExcessSharpe5d',
        'MinAbnCorr',
        'MinAmtKurt20d',
        'MinAmtMidChg',
        'MinAmtMidSkew',
        'MinAmtMidStd',
        'MinAmtSkew10d',
        'MinBWS',
        'MinBWskew',
        'MinBWstd',
        'MinCloseCallAmt5maCorrSharpe',
        'MinCloseReSkew5d',
        'MinCorHighVolumeMax10d',
        'MinCorW',
        'MinCorrRank',
        'MinCorrRankMean',
        'MinCorrVolumeRetUp5d',
        'MinEMVA',
        'MinEMVANorm',
        'MinERRC',
        'MinFW',
        'MinHLS',
        'MinHVSDis',
        'MinHVSmin',
        'MinHVV',
        'MinIdx500Corr',
        'MinIndexCorr',
        'MinLSV',
        'MinMACDNumDiffMean_1_1',
        'MinMACDNumDiffRank_5_5',
        'MinPMAmpVolume5d',
        'MinPRRC',
        'MinPVCS',
        'MinPmR',
        'MinRRCDis',
        'MinRRCs',
        'MinRSTstd',
        'MinRVM',
        'MinRVS',
        'MinReSkewLast120_10d',
        'MinReSkewLast120_20d',
        'MinReSkewLast120_5d',
        'MinRetVolKurtRank_5_1',
        'MinRetVolKurtRaw_5_5',
        'MinRetVolMaxSr_1_1',
        'MinRetVolMaxSr_1_5',
        'MinRetVolMaxStd_1_1',
        'MinRetVolSkewMean_5_5',
        'MinRetVolSkewRank_5_1',
        'MinRetVolSkewRank_5_5',
        'MinRetVolStdSr_1_1',
        'MinReturnVolUp2Down5d',
        'MinSkW',
        'MinSkew40d',
        'MinSmartFoolRatioMean',
        'MinStdW',
        'MinTAW',
        'MinTTD',
        'MinTTM',
        'MinTimeHighLow_20',
        'MinTopTailCost',
        'MinTopV',
        'MinTopVolRate',
        'MinUBK',
        'MinUBM',
        'MinUBS',
        'MinUBSR',
        'MinVB10',
        'MinVBR',
        'MinVRCExcess5d',
        'MinVVCorrRank',
        'MinVVCorrRankStd',
        'MinVVRankCorrStd',
        'MinVolRe',
        'MinVwapARC2VRCExcessSharpe20d',
        'MinVwapRV',
        'MinVwapRVskew',
        'MinWAC',
        'MinWR_20_80_5d',
        'MinWeightVolReRatio',
        'MinWeightVolReSkew',
        'MinWeightVolReSwing',
        'Min_ACD',
        'Min_PredictReturn2Volume',
        'Min_PredictReturnMean',
        'Min_RelativeDownReturn',
        'Min_UpRange',
        'Minute30CloseVolumeCorr',
        'Minute30m5dVolumeHHI',
        'MinuteALTKurt',
        'MinuteAmtCV3d',
        'MinuteAmtRetCor5d',
        'MinuteAmtStdSwing',
        'MinuteCloseCallAuctionTurnoverStdChange180d',
        'MinuteCloseDiff',
        'MinuteCloseMMT',
        'MinuteCloseMomentumSharpe',
        'MinuteCloseResist',
        'MinuteCloseSmartGame',
        'MinuteCloseTurn',
        'MinuteCloseTurnCorr',
        'MinuteCloseTurnEWMA',
        'MinuteCloseTurnPlus',
        'MinuteCloseTurnR',
        'MinuteCloseTurnREWMA',
        'MinuteCloseTurnRSharpe',
        'MinuteCloseTurnRSharpe10',
        'MinuteCloseTurnRev',
        'MinuteCloseTurnSharp',
        'MinuteCloseTurnoverStd',
        'MinuteCloseUpVar',
        'MinuteCloseWREWMA',
        'MinuteCloseWRVolume',
        'MinuteCorrRank',
        'MinuteDCDTA5d',
        'MinuteDownVolatilityRatio20d',
        'MinuteEODRetDrawdownRatioSharpe',
        'MinuteEODSkewness120Min',
        'MinuteEODSortinoRatioSharpe',
        'MinuteEODVolWeightedLongShortPowerSharpe',
        'MinuteEODVolumeWeightedReturnSharpe',
        'MinuteGroupReBias5d',
        'MinuteHighLowRtnVolDiff',
        'MinuteIdioSkew5d',
        'MinuteIlliqVwapClose5d',
        'MinuteLast30mPriceVolRefineMean10d',
        'MinuteLastHourMDDMCLIMBstd20d',
        'MinuteLastHourMaxClimb20dSR',
        'MinuteLastHourSkewness40d',
        'MinuteLastTurn20std',
        'MinuteLastVolumeRank5std',
        'MinuteMADistanceMA',
        'MinutePVCorrMin',
        'MinuteRelativeUpVar',
        'MinuteRetLastHrSkew',
        'MinuteRetSkewnessSharpe',
        'MinuteRetTurnRho',
        'MinuteRetVolMultSkew',
        'MinuteRetVolMultSkewSharpe',
        'MinuteReturnAutocorr5d',
        'MinuteReturnDiffStdSharpe',
        'MinuteReturnSkew',
        'MinuteSwing',
        'MinuteTERtnVRatio',
        'MinuteTLSTRvs',
        'MinuteTLSVRatio',
        'MinuteTPVDeltaCorr',
        'MinuteTRtnVGRank',
        'MinuteTRtnVGStdRank',
        'MinuteTRtnVRatioRank',
        'MinuteTSD',
        'MinuteTTLSStdRank',
        'MinuteTWRSharpe20',
        'MinuteTWRSkew20',
        'MinuteTurnoverStdSharpe',
        'MinuteTurnoverVolSharpe',
        'MinuteUpVar',
        'MinuteVMASkew',
        'MinuteValidRet',
        'MinuteVolCVSkew10d',
        'MinuteVolVwapCorrCloseChg',
        'MinuteVolofVolumeHHI',
        'MinuteVolumeHHISharpe',
        'MinuteVolumeKurt',
        'MinuteVolumeStabilitySharpe',
        'MinuteVolumeStdSharpe',
        'MinuteWRMean',
        'MinuteliqAmtRatioSharpe20d',
        'MinuteliqSwingSharpe5d',
        'MinuteliqSwingStd5',
        'MomBigOrder3Day',
        'MomHigh2Low10d',
        'MomHighExclMorn20d',
        'MomW',
        'MoneyMaker',
        'NIGrowthZscore1y',
        'NI_SQ_IndustryRank',
        'NetProfitSurprise',
        'NetProfit_sq_TSRank8',
        'Netprofitmargin_q',
        'NetworkDegree',
        'NonstationaryPV',
        'NonstationaryPVSharp',
        'OBCVPema_10',
        'OCVPema_20',
        'ODPB_DIFF120',
        'ODPB_DIFF20',
        'ODPEG_DIFF120',
        'ODPEG_DIFF20',
        'OTC5std',
        'OpenAmt',
        'OpenPositionInHighLowWeightedByVol_Mean_5',
        'OperProfitTTMStandardGrowth',
        'OperRevTTMStandardGrowth',
        'OverBuySell_Mean_5',
        'PDPS_Hist2_120D',
        'PEAdj',
        'PROFIT_PER20',
        'PROFIT_PER60',
        'PROFIT_SUM20',
        'PROFIT_UP60',
        'PVMax',
        'PVTTurn180d',
        'PVTTurn5d',
        'PVTTurn60d',
        'PePercent240d',
        'PriceDiff',
        'ProfitNoticeIndRank',
        'Profitability_IndZscore',
        'QfaROE',
        'QfaYoyeps',
        'ROEStandardGrowth',
        'ROEWin',
        'RSI',
        'RTC',
        'RTurnGainMin',
        'RTurnGainStd',
        'RangeRetCorr20',
        'RankEBIT2TRIndustrialStability',
        'RankEBITPSChg',
        'RankP2UndistributedEPS',
        'RankPBDev',
        'RankPEChange',
        'RankRetEPSIndustrialStability',
        'RankRoAIndustrialStability',
        'RankinglistEffect',
        'Re300ReturnScore5D',
        'ReCorr20',
        'ReCorrMean5dRank',
        'ReStdUp2Down5d',
        'RelativeIndPEAS',
        'RelativeIndPEGAvg',
        'ReportScoreGrowth',
        'Ret10Max_CS60_Mean2Std10',
        'Ret2Drawdown_CS60_Mean2Std10',
        'Ret2RetLength_CS15_Bias10',
        'Ret2RetLength_CS15_Mean2Std10',
        'RetCorrTurnDelayPure',
        'RetCutCorrTurnDelay',
        'RetDiffStd_Mean2Std10',
        'RetMaxMinSum_Mean10',
        'RetMaxMinSum_SR5',
        'RetMktDevCorr',
        'RetRankStd10d',
        'RetSkewSharp',
        'RetSkew_CS120_Mean2Std10',
        'RetSkew_CS180_Mean2Std30',
        'RetSkew_CS60_Mean2Std10',
        'RetSkew_Mean2Std10',
        'RetSkew_Mean_5',
        'RetStdTurnCorr',
        'RetUpDownRatio_CS20_Mean5',
        'RetVolMultSharp_30',
        'RetVolProdSkewSharp_20',
        'RevSplit',
        'ReverseDistance',
        'ReverseMomentumDouble',
        'ReverseMomentumTriple',
        'RoeTTM_IndRank',
        'RtnVolGrowthRankDiff',
        'SPPI',
        'SectorIlliquidity',
        'SectorNotionalSharpe',
        'SectorPESharpe',
        'SellRtnSellMoneyDiffCorr',
        'SeperateBeforehandRet_30',
        'SeperateBeforehandRet_Normolized20',
        'ShoutCutILLIQ_10',
        'SimpleVolume',
        'SmallPlayersTurnover',
        'SmallPlayersTurnoverSharpe20d',
        'SmallPlayersVwap',
        'Smartmoney_amt_skew01505_rolling1_daily',
        'Smartmoney_close_trb0505_rolling3_daily',
        'Smartmoney_hlratio_ms0505_rolling1_daily',
        'Smartmoney_hlratio_rdm01505_rolling3_daily',
        'Smartmoney_hlratio_rdm0505_rolling3_daily',
        'StaVolDivRetUpdown',
        'StableRet',
        'StableVol',
        'SwingHighLowPriceCorr',
        'SwingToTurn',
        'SwingW',
        'TPVDeltaCorr',
        'TargetReturnDelta5d',
        'TickFactor_AccBuyKurt',
        'TickFactor_AccBuyStd',
        'TickFactor_ActBuyKurt',
        'TickFactor_ActBuyOrderStdRatio',
        'TickFactor_BuyOrderStd',
        'TickFactor_BuyOrderStdRatio',
        'TickFactor_MaxAccBuyStdRatio',
        'TickFactor_MaxActBuyOrderStdRatio',
        'TickFactor_MaxBuyOrderStdRatio',
        'TickFactor_MinAccBuyStdRatio',
        'TickFactor_MinActBuyOrderStdRatio',
        'TickFactor_MinBuyOrderStdRatio',
        'TickFactor_PassBuyOrderStdRatio',
        'TickFactor_RawAccBuyKurt',
        'TickFactor_RawAccBuyStdRatio',
        'TickFactor_RawActBuyOrderStdRatio',
        'TickFactor_RegActBuyOrderStdRatio',
        'TickFactor_RegBuyOrderStdRatio',
        'Tick_NewBuyOrderAmt',
        'Tick_NewBuyOrderAmt_std',
        'Tick_NewSellOrderAmt',
        'Tick_NewSellOrderAmt_std',
        'Tick_bsdiff_amt_std_top_ordercanceledvol_skew3_daily',
        'Tick_bsdiff_hl_tail_active_orderamt_cov3_daily',
        'Tick_bsdiff_hl_tail_passive_orderamt_corr3_daily',
        'Tick_bsdiff_hl_top_active_ordervol_cov1_daily',
        'Tick_bsdiff_hl_top_active_ordervol_cov3_daily',
        'Tick_bsdiff_illq_tail_active_orderamt_avg3_daily',
        'Tick_bsdiff_illq_tail_passive_orderamt_corr3_daily',
        'Tick_bsdiff_illq_tail_tradevol_corr3_daily',
        'Tick_bsdiff_illq_top_active_orderamt_cov3_daily',
        'Tick_bsdiff_illq_top_ordervol_cov3_daily',
        'Tick_bsdiff_illq_top_tradeamt_avg1_daily',
        'Tick_bsdiff_illq_top_tradevol_corr1_daily',
        'Tick_bsdiff_raw_active_ordervol_corr3_daily',
        'Tick_bsdiff_ret_skew_tail_active_orderamt_cov3_daily',
        'Tick_bsdiff_ret_skew_tail_ordercanceledamt_avg3_daily',
        'Tick_bsdiff_ret_skew_tail_ordervol_avg3_daily',
        'Tick_bsdiff_ret_skew_top_active_orderamt_skew3_daily',
        'Tick_bsdiff_ret_skew_top_passive_orderamt_corr3_daily',
        'Tick_bsdiff_ret_skew_top_tradenum_corr3_daily',
        'Tick_bsdiff_ret_std_tail_active_orderamt_corr3_daily',
        'Tick_bsdiff_ret_std_tail_passive_orderamt_corr3_daily',
        'Tick_bsdiff_ret_std_top_active_ordervol_corr3_daily',
        'Tick_bsdiff_ret_std_top_orderamt_avg3_daily',
        'Tick_bsdiff_ret_std_top_ordervol_corr3_daily',
        'Tick_bsdiff_ret_tail_orderamt_corr3_daily',
        'Tick_bsdiff_ret_tail_ordercanceledamt_cov3_daily',
        'Tick_bsdiff_ret_tail_passive_orderamt_cov3_daily',
        'Tick_bsdiff_ret_tail_passive_ordervol_corr1_daily',
        'Tick_bsdiff_ret_top_ordercanceledvol_cov1_daily',
        'Tick_bsdiff_ret_top_ordercanceledvol_cov3_daily',
        'Tick_bsdiff_ret_top_passive_orderamt_cov3_daily',
        'Tick_bsdiff_ret_top_tradenum_cov1_daily',
        'Tick_bsdiff_self_tail_active_orderamt_cov3_daily',
        'Tick_bsdiff_self_tail_ordercanceledvol_skew1_daily',
        'Tick_bsdiff_self_tail_tradeamt_std3_daily',
        'Tick_bsdiff_self_top_active_orderamt_cov3_daily',
        'Tick_bsdiff_self_top_ordercanceledamt_std3_daily',
        'TradeNumSkewDay',
        'TurnCV_10',
        'TurnCloseLowSharpe',
        'TurnCorrSharp',
        'TurnGain',
        'TurnHighClose',
        'TurnHighCloseSharpe',
        'TurnHighCloseSigma',
        'TurnNeuRetCorrSharp',
        'TurnPEAS',
        'TurnPEStd',
        'TurnRankPercent_1d_240d',
        'TurnoverSharpe',
        'TurnoverSharpe100d',
        'TwapVwapRet',
        'UpAmtKurt_Mean5',
        'UpDownVolatility',
        'UpHigh2VwapWeightedByVolume_SR20',
        'UpSpeed',
        'UpVolatilityRatio_20',
        'UpVwap2LowWeightedByVolume_SR20',
        'ValueDelay',
        'ValueGrowthChange60d',
        'ValueRefined',
        'Vol30HHI_Mean2Std10',
        'VolPctMeanRankDiffInExtremeUpDownRet_Mean5',
        'VolPriceCorr',
        'VolPriceFlyer',
        'VolPriceFlyerPlus',
        'VolPriceRunner',
        'VolRPriceRCorr20d',
        'VolRaiseMom5d',
        'VolRegIndexRsquare_20',
        'VolSurgeSharpe',
        'VolSwingRankCorr',
        'VolUpDownStdRatio_Mean_5',
        'VolaRatioOnBSlog3Day',
        'VolitilityMax',
        'VolitilityRelative',
        'VolumeRatioDown20d',
        'VolumeShortLongStdRatio',
        'VolumeStdBias',
        'VolumeStdHigh2Low20d',
        'VolumeStdHigh2Low5d',
        'VwapCloseAdj20d',
        'VwapRatio',
        'VwapRatioOnAmtPerTradeDay',
        'VwapReCorrMean10dRank',
        'VwapTurnStdRatio',
        'WQ016',
        'WQ_027',
        'WeightedDownUpSumRatio5d',
        'WinnerList_225',
        'ZaoYinTrader',
        'abnormal_coverage_nis',
        'alp10_alpuniv',
        'alp12_alpuniv',
        'alp22_alpuniv',
        'alp29_alpuniv',
        'alp3_alpuniv',
        'alphas_dongj_pct_chg_swing_combine',
        'amt_3d_120d_ratio_nis',
        'amt_size_corr_turn_nis',
        'asset_turnover_lvl_chg_nis',
        'buy_volume_exlarge_order_act_5d_inv_nis',
        'cashflow_multiple_lvl_chg_nis',
        'chgw_alpuniv',
        'chwg4',
        'chwg5',
        'close_vol_pct_prod_r20_nis',
        'core_alpuniv',
        'cs_resid_amt_std_15_nis',
        'cs_resid_turn_std_20_nis',
        'csad1',
        'csad_ftest',
        'dep_pure_nis',
        'dpEPS_F1YF2Y_lvl_chg60_nis',
        'dretvolnew_kurtmean_20_10_daily',
        'dretvolnew_skewmean_60_3_daily',
        'dretvvolnew_msmean_20_10_daily',
        'dretvvolnew_msmean_60_10_daily',
        'dretvvolnew_msmean_60_3_daily',
        'dretvvolnew_scmmean_20_10_daily',
        'dretvvolnew_scmmean_60_10_daily',
        'dretvvolnew_skewmean_20_10_daily',
        'dretvvolnew_skewmean_20_3_daily',
        'dretvvolnew_skewmean_60_10_daily',
        'duvol_derived_nis',
        'dwf_alpuniv',
        'egr_nis',
        'ep_per_nis',
        'eps_c2_lvl_chg_nis',
        'fddcom_alpuniv',
        'front_run_comb_nis',
        'gross_margin_lvl_chg_nis',
        'gross_profit_margin_lvl_chg_nis',
        'growth_alpuniv',
        'growth_by_def_nis',
        'growth_comb_nis',
        'gtja_pv105_nis',
        'gtja_pv110_nis',
        'gtja_pv130_nis',
        'gtja_pv140_nis',
        'gtja_pv16_nis',
        'gtja_pv179_nis',
        'gtja_pv1_nis',
        'gtja_pv32_nis',
        'gtja_pv62_nis',
        'gtja_pv64_nis',
        'gtja_pv83_nis',
        'ls_strength_nis',
        'mid_price_w_amt_r40_nis',
        'net_profit_c2_lvl_chg_nis',
        'net_profit_margin_lvl_chg_nis',
        'npm_qfa_lvl_chg_nis',
        'open2close_turn_ls_nis',
        'open_moneyflow_pct_volume_20d_nis',
        'optogr_qfa_nis',
        'org_num_75d_nis',
        'pe_F2YF1Y_inv_lvl_chg60_nis',
        'pe_ttm_nis',
        'pechgnew_alpuniv',
        'peg_F2YF1Y_inv_lvl_chg60_nis',
        'pegfy1chg_alpuniv',
        'price_bias_comb_nis',
        'profitchg_alpuniv',
        'pt_r2_20_r20_nis',
        'qfa_roe_alpuniv',
        'qfa_roe_lvl_chg_nis',
        'qfa_yoyop_nis',
        'qfa_yoyprofit_alpuniv',
        'qfa_yoysales_alpunivchg',
        'r2_current_20d_diff_nis',
        'rev_cvturn_max_nis',
        'rev_turn_liq_nis',
        'reversal_trade_count_20d_nis',
        'rnoa_nis',
        'roe_basic_alpunivchg',
        'roe_fa_avg_lvl_chg_nis',
        'roema_alpuniv',
        's_fa_netprofittoor_ttm_growth_nis',
        's_fa_roe_ttm_growth_nis',
        's_qfa_roe_growth_nis',
        'sdrkurt_nis',
        'sdvhhi_norm_nis',
        'sell_volume_small_order_act_1d_inv_nis',
        'sp_lvl_chg_nis',
        'su_tot_assets_1_12_nis',
        'tper_nis',
        'tptpchg_alpuniv',
        'trade_strength_last15_r20_nis',
        'turn_mvc_nis',
        'up_vol_ratio_40d_nis',
        'uretvolnew_stdstd_20_3_daily',
        'uretvvolnew_kurtmean_20_3_daily',
        'uretvvolnew_kurtskew_20_10_daily',
        'uretvvolnew_meanskew_60_10_daily',
        'uretvvolnew_msmean_20_10_daily',
        'uretvvolnew_msstd_60_10_daily',
        'uretvvolnew_msstd_60_3_daily',
        'uretvvolnew_mstb_60_10_daily',
        'uretvvolnew_skewmean_20_10_daily',
        'uretvvolnew_skewmean_20_3_daily',
        'uretvvolnew_skewmean_60_10_daily',
        'uretvvolnew_stdskew_60_10_daily',
        'valuecom_alpuniv',
        'vol_up_nis',
        'volume_hhi_nis',
        'volume_skew_nis',
        'yoynetprofit_alpunivchg',
        'zhy_factor_24',
        'zhy_factor_56',
        'zhy_factor_61',
        'zhy_factor_63',
        'zhy_factor_64',
        'zhy_factor_65',
        'zhy_factor_72',
        'zhy_factor_73',
    ]
    factor_address = '/data/user/015518/quant_data/qualified_factor/x_day_lib/20181231/'
    middle_address = '/data/user/015836/model/temp20200513/'

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
    neutralize_fill = 'mad'
    #mv, mad, norm, uniform
    standardize_method = 'mv'

    groups = 10

    factor_preprocess(factor_list, factor_address, middle_address, start_date, end_date, price_type, future_days,
                      factor_complete_limit, factor_diversity_limit, winsorize_method, winsorize_alpha, neutralize_ind,
                      neutralize_method, neutralize_fill, standardize_method, groups)


    def calc_factor_turn2(self, factor_pool_address=None, factor_group_address=None, factor_turn_address=None):

        factor_pool_address = self.middle_address if factor_pool_address is None else factor_pool_address
        factor_group_address = self.middle_address if factor_group_address is None else factor_group_address
        factor_turn_address = self.middle_address if factor_turn_address is None else factor_turn_address

        for date in tqdm(self.date_list):

            factor_pool = np.load('%s%s %s.npy' % (factor_pool_address, 'factor_pool', date))
            factor_group = np.load('%s%s %s.npy' % (factor_group_address, 'factor_group', date))

            code_valid_num = self.code_valid_num[self.date_list.index(date)]


            if date == self.date_list[0]:
                groups = int(np.nanmax(factor_group))
                factor_turn = np.full((groups, factor_group.shape[0]), np.nan)
            else:
                factor_turn = np.r_['0,2', tuple(np.abs((factor_group == x) * 1. - (gl == x) * 1.).sum(axis=1)
                                                 for x in range(1, groups + 1))]
                factor_turn /= (code_valid_num + vl) / 2
                factor_turn[:, ~ factor_pool | ~ pl] = np.nan

            gl = factor_group
            pl = factor_pool
            vl = code_valid_num

            np.save(factor_turn_address + 'factor_turn ' + str(date), factor_turn)






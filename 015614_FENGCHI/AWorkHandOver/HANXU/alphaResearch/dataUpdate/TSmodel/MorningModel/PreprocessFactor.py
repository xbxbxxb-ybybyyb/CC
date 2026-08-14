import os
import re
import sys

import bottleneck
import gc
import numpy as np
import pandas as pd
from numba import njit, float64
from scipy.stats import norm, boxcox

sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.stockList import trans_windcode2int
from dataApi.tradeDate import get_pre_trade_date, get_date_range, trade_minutes, get_trade_date_interval, \
    get_recent_trade_date


def get_minute_pickle_latest_date(factor, address='/data/group/800080/PanelMinDataForZT/stock/'):
    latest = sorted([int(x[:6]) for x in os.listdir(f'{address}/{factor}')
                     if re.match('^\d{6}_' + factor + '.pkl$', x)])[-1]
    latest = pd.read_pickle(f'{address}/{factor}/{latest}_{factor}.pkl').index[-1]
    latest = int(latest.date().strftime('%Y%m%d'))
    return latest


def get_minute_pickle(factor, date_list, code_list=None,
                      address='/data/group/800080/PanelMinDataForZT/stock/', type='stock'):
    if type == 'bench':
        address = address + '/../index/'

    start_date = date_list[0]
    end_date = date_list[-1]

    month_list = sorted(list(set(get_date_range(start_date, end_date, 'M') + [end_date])))
    short_month_list = sorted(list({x // 100 for x in month_list}))
    month_start = get_recent_trade_date(short_month_list[0] * 100)
    month_end = get_recent_trade_date(short_month_list[-1] * 100)

    start_keep = get_trade_date_interval(start_date, month_start) * 242
    end_keep = (get_trade_date_interval(end_date, month_end) + 1) * 242
    df_list = [pd.read_pickle('%s/%s/%s_%s.pkl' % (address, factor, x, factor)) for x in short_month_list]
    df_list[-1] = df_list[-1].iloc[:end_keep] if len(month_list) > 1 else df_list[-1].iloc[start_keep: end_keep]
    df_list[0] = df_list[0].iloc[start_keep:] if len(month_list) > 1 else df_list[0]

    df = pd.concat(df_list)
    df.columns = df.columns.map(trans_windcode2int)
    df = df.reindex(columns=code_list)
    df.index = pd.MultiIndex.from_product([date_list, trade_minutes])
    return df


def get_morning_factor_list(restore=False, factor_address='/data/group/800442/800319/HFfactor/MorningFactor/'):
    if restore:
        data_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
        factor_list1 = {x[:-4] for x in os.listdir(data_address) if not re.match('^Fix1[0134][03]0_', x)}
        factor_list2 = {x[:-4] for x in os.listdir(data_address) if re.match('^Fix1430_', x)}
        factor_list = sorted(list((factor_list1 | factor_list2) - {''}))
        if not os.path.exists(factor_address):
            os.makedirs(factor_address)
        pd.to_pickle(factor_list, f'{factor_address}/factor_list.pkl')
    else:
        factor_list = pd.read_pickle(f'{factor_address}/factor_list.pkl')
    factor_list = sorted(list(set(factor_list) - {'Governance'}))
    return factor_list


def get_fix_factor_list(restore=False, factor_address='/data/group/800442/800319/HFfactor/MorningFactorFixEnd/'):
    if restore:
        load_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
        freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
        factor_list = sorted(list({x[8:-4] for x in os.listdir(
            load_address) if re.match('^Fix1[0134][03]0_', x)}))
        factor_list = [x for x in factor_list if len([y for y in os.listdir(
            load_address) if x in y and len(x) == len(y) - 12]) == len(freq)]
        pd.to_pickle(factor_list, f'{factor_address}/fix_factor_list.pkl')
    else:
        factor_list = pd.read_pickle(f'{factor_address}/fix_factor_list.pkl')
    return factor_list


def load_factor(name, date_list, code_list, load_address='/data/group/800002/alpha_factor/lib/x_factor_lib/'):
    df = pd.read_pickle('%s/%s.pkl' % (load_address, name))
    valid_code = [x for x in df.columns if isinstance(x, str)]
    valid_code = [x for x in valid_code if re.match('^[036]\d{5}.S[HZ]$', x)]
    df = df.reindex(columns=valid_code)
    df.columns = df.columns.map(trans_windcode2int)
    df.index = df.index.map(int)
    df = df.reindex(date_list, code_list).values
    if (np.isfinite(df[-1]).sum() == 0) & (name not in ('QfaROE', 'QfaYoyeps')):
        raise ValueError("New data is not arriving.")
    return df


def load_factor_tmr(name, date_list, code_list, load_address='/data/group/800002/alpha_factor/lib/x_factor_lib/'):
    df = pd.read_pickle('%s/%s.pkl' % (load_address, name))
    valid_code = [x for x in df.columns if isinstance(x, str)]
    valid_code = [x for x in valid_code if re.match('^[036]\d{5}.S[HZ]$', x)]
    df = df.reindex(columns=valid_code)
    df.columns = df.columns.map(trans_windcode2int)
    df.index = df.index.map(int)
    date_list_lag = get_date_range(get_pre_trade_date(date_list[0], -1), get_pre_trade_date(date_list[-1], -1))
    df = df.reindex(date_list_lag, code_list).values
    if (np.isfinite(df[-1]).sum() == 0) & (name not in ('QfaROE', 'QfaYoyeps')):
        raise ValueError("New data is not arriving.")
    return df

def find_trade_min(sign_min, delay_min=1, order_keep_min=5, twap_mode=False):
    sign_min = sign_min if sign_min < 242 else trade_minutes.index(sign_min)
    trade_min = [sign_min + (delay_min if sign_min else 0) + x for x in range(order_keep_min)]
    if twap_mode:
        if trade_min[0] >= 238:
            trade_min = [241] * order_keep_min
        elif trade_min[-1] >= 238:
            _head_min = list(range(trade_min[0], 239))
            trade_min = _head_min + [241] * (order_keep_min - len(_head_min))
    else:
        if trade_min[0] >= 238:
            trade_min = [240] * (order_keep_min - 1) + [241]
        elif trade_min[-1] >= 238:
            _head_min = list(range(trade_min[0], 239))
            trade_min = _head_min + [240] * (order_keep_min - 1 - len(_head_min)) + [241]
    return trade_min


def load_future(date_list, code_list, future_days=1, bar_min=930, delay_min=1, order_keep_min=30, twap=False, tmr=True):
    future_days = [future_days] if isinstance(future_days, int) else future_days
    max_future_day = max(*(future_days + [0]))

    start_date = get_pre_trade_date(date_list[0], -tmr)
    end_date = get_pre_trade_date(date_list[-1], - tmr - max_future_day)
    latest = get_minute_pickle_latest_date('amt')
    use_date_list = get_date_range(start_date, min(end_date, latest))

    if isinstance(bar_min, int):
        bar_min = [bar_min]
    idx = np.arange(len(use_date_list))[:, None, None] * 242 + np.asanyarray([find_trade_min(
        x, delay_min, order_keep_min, twap) for x in bar_min])[None, :, :]

    _limit_status = get_minute_pickle('limit_status', use_date_list, code_list)
    limit_status = _limit_status.shift(1)
    limit_status.iloc[::242] = _limit_status.iloc[::242]
    del _limit_status
    gc.collect()
    limit_status = limit_status.values[idx]

    if twap:
        close_adj = get_minute_pickle('close_adj', use_date_list, code_list).values[idx]
        pr_buy = np.nanmean(np.where(limit_status[:-max_future_day] == 1, np.nan, close_adj[:-max_future_day]), axis=2)
        # pr_sell = np.nanmean(np.where(limit_status[future_days:] == -1, np.nan, close_adj[future_days:]), axis=2)
        pr_sell = np.r_[
            '0,3', tuple(np.nanmean(close_adj[x: x - max_future_day if x < max_future_day else None], axis=2)
                         for x in future_days)].mean(axis=0)
        del close_adj
        gc.collect()
        ret = pr_sell / pr_buy - 1
    else:
        volume = get_minute_pickle('volume', use_date_list, code_list).values[idx]
        vol_buy = np.nansum(np.where(limit_status[:-max_future_day] == 1, 0, volume[:-max_future_day]), axis=2)
        vol_buy[vol_buy < 100] = np.nan
        # vol_sell = np.nanmean(np.where(limit_status[future_days:] == -1, 0, volume[future_days:]), axis=2)
        vol_sell = {}
        for x in future_days:
            vol_sell[x] = np.nansum(volume[x: x - max_future_day if x < max_future_day else None], axis=2)
            vol_sell[x][vol_sell[x] < 100] = np.nan
        del volume
        gc.collect()
        amt = get_minute_pickle('amt', use_date_list, code_list).values[idx]
        adjfactor = get_minute_pickle('adjfactor', use_date_list, code_list).values[idx]
        amt *= adjfactor
        del adjfactor
        gc.collect()
        amt_buy = np.nansum(np.where(limit_status[:-max_future_day] == 1, 0, amt[:-max_future_day]), axis=2)
        amt_sell = {}
        for x in future_days:
            amt_sell[x] = np.nansum(amt[x: x - max_future_day if x < max_future_day else None], axis=2)
        del amt
        gc.collect()
        ret = {}
        for x in future_days:
            ret[x] = amt_sell[x] * vol_buy / vol_sell[x] / amt_buy - 1
            # ret[x][limit_status[:-max_future_day, :, 0] != 0] = np.nan
        ret = np.r_['0,3', tuple(ret[x] for x in future_days)].mean(axis=0)
    if ret.shape[1] == 1:
        ret = ret[:, 0]
    return ret


def load_future_fix_end(date_list, code_list, future_day=1, buy_min=1000,
                        sell_min=1000, delay_min=1, order_keep_min=30, tmr=True):
    start_date = get_pre_trade_date(date_list[0], -tmr)
    end_date = get_pre_trade_date(date_list[-1], - tmr - future_day)
    latest = get_minute_pickle_latest_date('amt')
    use_date_list = get_date_range(start_date, min(end_date, latest))
    buy_idx = np.arange(len(use_date_list))[:, None] * 242 + np.asanyarray(find_trade_min(
        buy_min, delay_min, order_keep_min, tmr))
    sell_idx = (np.arange(len(use_date_list))[:, None]) * 242 + np.asanyarray(find_trade_min(
        sell_min, delay_min, order_keep_min, tmr))
    buy_idx = buy_idx[:-future_day]
    sell_idx = sell_idx[future_day:]
    _limit_status = get_minute_pickle('limit_status', use_date_list, code_list)
    limit_status = _limit_status.shift(1)
    limit_status.iloc[::242] = _limit_status.iloc[::242]
    del _limit_status
    gc.collect()
    limit_status = limit_status.values[buy_idx]
    close_adj = get_minute_pickle('close_adj', use_date_list, code_list).values
    pr_buy = np.nanmean(np.where(limit_status == 1, np.nan, close_adj[buy_idx]), axis=1)
    pr_sell = np.nanmean(close_adj[sell_idx], axis=1)
    del close_adj
    gc.collect()
    ret = pr_sell / pr_buy - 1
    return ret


def winsorize(arr, axis=-1, method='mad', out='raw_rank', alpha=0.01):
    arr = arr.copy()
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

    elif method == 'box':

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
    arr = arr.copy()
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
        std[std == 0] = np.nan
        arr -= mean
        arr /= std
        arr = arr.swapaxes(0, axis)
        return arr

    elif method == 'uniform':
        arr = arr.swapaxes(0, axis).astype(float)
        arr = bottleneck.nanrankdata(arr, axis=0)
        arr /= np.nanmax(arr, axis=0)
        arr = arr.swapaxes(0, axis)
        return arr

    elif (len(method) > 7) & (method[:7] == 'uniform'):
        t1 = int(method[7:9]) / 100
        t2 = int(method[10:12]) / 100
        arr = arr.swapaxes(0, axis).astype(float)
        arr = bottleneck.nanrankdata(arr, axis=0)
        arr /= np.nanmax(arr, axis=0)
        arr[arr <= 1 - t1] *= (1 - t2) / (1 - t1)
        arr[arr > 1 - t1] = 1 - (t2 / t1) * (1 - arr[arr > 1 - t1])
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


@njit(float64[:, :](float64[:, :, :], float64[:, :]))
def ols_residual(X, Y):
    residual = np.empty_like(Y)
    for j in range(X.shape[1]):
        x = X[:, j, :]
        y = Y[j, :]
        valid = (np.isfinite(x).sum(axis=0) == x.shape[0]) & np.isfinite(y)
        x = x[:, valid]
        y = y[valid]
        r = np.full(Y.shape[1], np.nan)
        xx = x @ x.T
        if np.linalg.matrix_rank(xx) == xx.shape[0]:
            r[valid] = y - x.T @ np.linalg.inv(xx) @ x @ y
        residual[j] = r
    return residual


def ols1_residual(X, Y):
    X, Y = X.copy(), Y.copy()
    valid = np.isfinite(X) & np.isfinite(Y)
    X[~ valid], Y[~ valid] = np.nan, np.nan
    X -= np.nanmean(X, axis=1, keepdims=True)
    Y -= np.nanmean(Y, axis=1, keepdims=True)
    X /= np.nanstd(X, axis=1, keepdims=True)
    Y /= np.nanstd(X, axis=1, keepdims=True)
    beta = np.nansum(X * Y, axis=1, keepdims=True) / np.sum(
        valid, axis=1, keepdims=True)
    beta[~ np.isfinite(beta)] = np.nan
    residual = Y - X * beta
    return residual


def ols2_residual(X, Y):
    X = X.astype('float64')
    Y = Y.astype('float64')
    finite = np.isfinite(X).all(axis=0) & np.isfinite(Y)
    finite_d = finite.sum(axis=1)
    X[:, ~ finite] = 0
    Y[~ finite] = 0
    Y -= (Y.sum(axis=1) / finite_d)[:, None]
    X -= (X.sum(axis=2) / finite_d)[:, :, None]
    X[:, ~ finite] = 0
    Y[~ finite] = 0
    Vxi = (X[1:] ** 2).sum(axis=2)
    Byi = np.where(Vxi > 0, (Y * X[1:]).sum(axis=2) / Vxi, 0)
    Bmi = np.where(Vxi > 0, (X[0] * X[1:]).sum(axis=2) / Vxi, 0)
    Me = X[0] - (Bmi[:, :, None] * X[1:]).sum(axis=0)
    Bym = (Y * Me).sum(axis=1) / (Me ** 2).sum(axis=1)
    res = Y - (Byi[:, :, None] * X[1:]).sum(axis=0) - Bym[:, None] * Me
    res[~ finite] = np.nan
    return res


def neutralize(arr, ind, mv, mv_ind, stock_pool, method='ols', fill='ind_mad'):
    if method is not None:
        arr = standardize(arr)

    if method == 'ols':
        if mv_ind.ndim == 3:
            arr = ols2_residual(mv_ind, arr)
        else:
            arr = ols1_residual(mv_ind, arr)
    elif method in ('mad', 'mv', 'uniform', 'normal'):
        for i in range(ind.shape[0]):
            temp = standardize(np.ma.array(arr, mask=~ind[i], fill_value=np.nan).filled(), axis=-1, method=method)
            temp_mv = standardize(np.ma.array(mv, mask=~ind[i], fill_value=np.nan).filled(), axis=-1, method=method)
            arr[ind[i]] = temp[ind[i]]
            mv[ind[i]] = temp_mv[ind[i]]
        arr = ols1_residual(mv, arr)

    elif method is not None:
        raise ValueError("neutralize method must be ols, mad, mv, uniform, normal or None")

    if fill == 'ind_mad':
        for i in range(ind.shape[0]):
            arr[ind[i] & ~ np.isfinite(arr) & stock_pool] = np.nanmedian(np.ma.array(
                arr, mask=~ind[i], fill_value=np.nan).filled(), axis=1)[:, None].repeat(
                arr.shape[1], axis=1)[ind[i] & ~ np.isfinite(arr) & stock_pool]
        arr[stock_pool & ~ np.isfinite(arr)] = np.nan

    elif fill == 'ind_mean':
        for i in range(ind.shape[0]):
            arr[ind[i] & ~ np.isfinite(arr) & stock_pool] = np.nanmean(np.ma.array(
                arr, mask=~ind[i], fill_value=np.nan).filled(), axis=1)[:, None].repeat(
                arr.shape[1], axis=1)[ind[i] & ~ np.isfinite(arr) & stock_pool]
        arr[stock_pool & ~ np.isfinite(arr)] = np.nan

    elif fill == 'mean':
        arr[~ np.isfinite(arr)] = np.nanmean(arr, axis=1)[~ np.isfinite(arr)]
        arr[stock_pool & ~ np.isfinite(arr)] = np.nan

    elif fill is not None:
        raise ValueError("fill method must be ind_mad, ind_mean, mean or None")

    return arr


def ind_dual_mean(arr, ind, stock_pool):
    arr = arr.copy()
    finite = np.isfinite(arr) & stock_pool
    arr[~ finite] = 0
    num = np.empty(arr.shape, dtype='float32')
    for i in range(ind.shape[0]):
        arr[ind[i]] -= np.sum(np.ma.array(
            arr, mask=~ind[i], fill_value=0).filled(), axis=1)[:, None].repeat(arr.shape[1], axis=1)[ind[i]]
        num[ind[i]] = np.sum(ind[i] & finite, axis=1, dtype='float32')[:, None].repeat(arr.shape[1], axis=1)[ind[i]]
    num[num < 3] = np.nan
    arr /= 1 - num
    arr[stock_pool & ~ np.isfinite(arr)] = 0
    return arr


def ind_double_rank(arr, ind, stock_pool):
    arr = arr.copy()
    finite = np.isfinite(arr) & stock_pool
    arr[~ finite] = np.nan
    arr_ind = np.empty((ind.shape[0], ind.shape[1]), dtype=arr.dtype)
    for i in range(ind.shape[0]):
        arr_ind[i] = np.nanmean(np.ma.array(arr, mask=~ind[i], fill_value=np.nan).filled(), axis=1)
    arr_ind = bottleneck.nanrankdata(arr_ind, axis=0).astype(arr.dtype) / np.isfinite(arr_ind).sum(axis=0,
                                                                                                   keepdims=True)
    arr = bottleneck.nanrankdata(arr, axis=1) / finite.sum(axis=1, keepdims=True)
    for i in range(ind.shape[0]):
        arr[ind[i]] += arr_ind[i, :, None].repeat(arr.shape[1], axis=1)[ind[i]]
    arr -= 1
    arr[stock_pool & ~ np.isfinite(arr)] = 0
    return arr


def corrcoef(X, y, axis=-1):
    X = X.copy()
    y = y.copy()
    X[~ (np.isfinite(y) & np.isfinite(X))] = np.nan
    y[~ (np.isfinite(y) & np.isfinite(X))] = np.nan
    X = X - np.nanmean(X, axis=axis)[:, None]
    y = y - np.nanmean(y, axis=axis)[:, None]
    multi = np.nanmean(X * y, axis=axis) / (np.nanstd(X, axis=axis) * np.nanstd(y, axis=axis))
    multi[np.isinf(multi)] = np.nan
    return multi


def pre_ts(d_cf, standardize_days=40, test_drop_days=43, clip=6):
    d_cn = np.isfinite(d_cf)
    d_cf[~ d_cn] = 0
    d_cf2 = d_cf ** 2

    rd_cf = np.lib.stride_tricks.as_strided(d_cf, shape=(
        d_cf.shape[0] - standardize_days + 1, standardize_days, d_cf.shape[1]), strides=(
        d_cf.strides[0], d_cf.strides[0], d_cf.strides[1])).sum(axis=1)

    rd_cf2 = np.lib.stride_tricks.as_strided(d_cf2, shape=(
        d_cf2.shape[0] - standardize_days + 1, standardize_days, d_cf2.shape[1]), strides=(
        d_cf2.strides[0], d_cf2.strides[0], d_cf2.strides[1])).sum(axis=1)

    rd_cn = np.lib.stride_tricks.as_strided(d_cn, shape=(
        d_cn.shape[0] - standardize_days + 1, standardize_days, d_cn.shape[1]), strides=(
        d_cn.strides[0], d_cn.strides[0], d_cn.strides[1])).sum(axis=1).astype(float)

    rd_cn[rd_cn < standardize_days / 2] = np.nan
    d_cf[~ d_cn] = np.nan

    rd_mean = (rd_cf / rd_cn)[test_drop_days - standardize_days: -1]
    rd_std = (((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5)[test_drop_days - standardize_days: -1]
    rd_std[rd_std == 0] = np.nan

    d_cf = (d_cf[test_drop_days:] - rd_mean) / rd_std
    if clip:
        d_cf = d_cf.clip(-clip, clip)
    return d_cf


def pre_cs(factor, stock_pool, winsor=True, standard=True, neutral=True, ind=None, mv=None, mv_ind=None):
    factor_finite = np.isfinite(factor)
    factor[~ (factor_finite & stock_pool)] = np.nan
    if winsor:
        factor = winsorize(factor, method='mad', alpha=0.01)
    if standard:
        factor = standardize(factor)
    if neutral:
        factor = neutralize(factor, ind, mv, mv_ind, stock_pool,
                            method='ols', fill='ind_mad')
        factor = standardize(factor, method='mv')
    factor[stock_pool & ~ np.isfinite(factor)] = np.nan
    return factor


def stats_range(date_index, date_list):
    date_list = np.asanyarray(date_list)
    date_index = np.asanyarray(date_index + [len(date_list)])
    start = date_list[date_index[:-1]]
    end = date_list[date_index[1:] - 1]
    return start, end


def calc_corr(x, y, x2, y2, xy, n):
    corr = (xy - x * y / n) / ((x2 - x ** 2 / n) * (y2 - y ** 2 / n)) ** 0.5
    corr = np.where(np.isfinite(corr), corr, 0)
    corr = corr if corr.size > 1 else corr.item()
    return corr

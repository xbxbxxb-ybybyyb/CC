from collections import Counter
from collections import OrderedDict

import bottleneck
import numpy as np
import pandas as pd
import scipy.stats as sps

from HFfactor.MinFactorSuper.Utility.ExtendNumpy import search_index
from dataApi.getData import get_daily_1factor
from dataApi.stockList import trans_windcode2int, trans_int2windcode
from dataApi.tradeDate import get_date_range, get_pre_trade_date, \
    get_trade_date_interval, get_recent_trade_date


class ArrReshape(object):

    def to2d(self, arr):
        self.freq = arr.shape[1]
        return arr.reshape(arr.shape[0] * arr.shape[1], arr.shape[2])

    def to3d(self, arr):
        return arr.reshape(arr.shape[0] // self.freq, self.freq, arr.shape[1])


def dt_future(x, m):
    ar = ArrReshape()
    return ar.to3d(np.pad(ar.to2d(x)[m:], ((0, m), (0, 0)), mode='constant', constant_values=np.nan))


def winsorize(arr, axis=-1, out='raw_rank', alpha=0.01):
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


def get_minute_data(factor, date_list, code_list=None,
                    address='/data/group/800080/PanelMinDataForZT/stock/', ignore_error=False):
    start_date = date_list[0]
    end_date = date_list[-1]
    row = 242 * len(date_list)

    month_list = sorted(list(set(get_date_range(start_date, end_date, 'M') + [end_date])))
    short_month_list = sorted(list({x // 100 for x in month_list}))
    month_dates = Counter([x // 100 for x in date_list])
    month_start = get_recent_trade_date(short_month_list[0] * 100)
    month_end = get_recent_trade_date(short_month_list[-1] * 100)

    start_keep = get_trade_date_interval(start_date, month_start) * 242
    end_keep = (get_trade_date_interval(end_date, month_end) + 1) * 242

    df = pd.read_pickle('%s/%s/%s_%s.pkl' % (address, factor, short_month_list[-1], factor))
    df = df.iloc[:end_keep] if len(month_list) > 1 else df.iloc[start_keep: end_keep]
    use_code_list = [trans_int2windcode(x) for x in code_list] if code_list else df.columns.to_list()
    col = len(use_code_list)

    arr = np.empty((row, col), dtype=np.float64)
    r_num = row
    pre_r_num = r_num - month_dates[short_month_list[-1]] * 242
    error_len = r_num - pre_r_num - len(df)
    if error_len != 0:
        if ignore_error:
            print(f'ERROR: {factor}_{short_month_list[-1]} minute data incomplete, lack {error_len / 242} days.')
            df = df.head(r_num - pre_r_num)
            r_num = pre_r_num + len(df)
        else:
            raise ValueError(f'{factor}_{short_month_list[-1]} minute data incomplete, lack {error_len / 242} days.')

    if code_list:
        code_index = search_index(use_code_list, df.columns.to_list())
        used_codes = code_index.data[~code_index.mask]
        unused_codes = sorted(list(set(range(col)) - set(used_codes)))
        arr[pre_r_num: r_num, code_index.data[~code_index.mask]] = df.values[:, ~code_index.mask]
        arr[pre_r_num: r_num, unused_codes] = np.nan
    else:
        arr[pre_r_num: r_num] = df.values

    for j in reversed(range(len(month_list) - 1)):
        df = pd.read_pickle('%s/%s/%s_%s.pkl' % (address, factor, short_month_list[j], factor))
        if not j:
            df = df.iloc[start_keep:]
        r_num = pre_r_num
        pre_r_num = r_num - month_dates[short_month_list[j]] * 242

        error_len = r_num - pre_r_num - len(df)
        if error_len != 0:
            if ignore_error:
                print(f'ERROR: {factor}_{short_month_list[j]} minute data incomplete, lack {error_len / 242} days.')
                df = df.head(r_num - pre_r_num)
                r_num = pre_r_num + len(df)
            else:
                raise ValueError(f'{factor}_{short_month_list[j]} minute data incomplete, lack {error_len / 242} days.')

        code_index = search_index(use_code_list, df.columns.to_list())
        used_codes = code_index.data[~code_index.mask]
        unused_codes = sorted(list(set(range(col)) - set(used_codes)))
        arr[pre_r_num: r_num, used_codes] = df.values[:, ~code_index.mask]
        arr[pre_r_num: r_num, unused_codes] = np.nan
    arr = arr.reshape(-1, 242, col)
    if code_list:
        return arr
    else:
        use_code_list = [trans_windcode2int(x) for x in use_code_list]
        return arr, use_code_list


def clean_minute_data(name, date_list, code_list, stock_pool):
    data = get_minute_data(name, date_list, code_list)
    data[~ stock_pool[:, None].repeat(data.shape[1], axis=1)] = np.nan
    return data


def clean_daily_data(name, date_list, code_list, stock_pool, lag=False):
    date_list = get_date_range(get_pre_trade_date(date_list[0]),
                               get_pre_trade_date(date_list[-1])) if lag else date_list
    data = get_daily_1factor(name, date_list, code_list).values
    data[~ stock_pool] = np.nan
    return data


def check_data(arr):
    total_num = arr.size
    inf_num = np.isinf(arr).sum()
    nan_num = np.isnan(arr).sum()
    zero_num = (arr == 0).sum()
    arr = arr[np.isfinite(arr)]
    max_value = arr.max()
    min_value = arr.min()
    if max_value * min_value == 0:
        arr = arr[arr != 0]
        if max_value == 0:
            max_value = arr.max()
        if min_value == 0:
            min_value = arr.min()
    valid_num = arr.shape[0]
    mean = arr.mean()
    median = np.median(arr)
    std = arr.std(ddof=1)
    mv_max = mean + 3 * std
    mv_min = mean - 3 * std
    med = np.nanmedian(np.fabs(arr - median))
    med_max = median + 3 * 1.483 * med
    med_min = median - 3 * 1.483 * med
    mv_max_excess = (arr > mv_max).sum() / valid_num
    mv_min_excess = (arr < mv_min).sum() / valid_num
    med_max_excess = (arr > med_max).sum() / valid_num
    med_min_excess = (arr < med_min).sum() / valid_num
    skew = sps.skew(arr, bias=False, nan_policy='omit')
    kurt = sps.kurtosis(arr, fisher=True, bias=False, nan_policy='omit')
    result = OrderedDict()
    result['total_num'] = total_num
    result['inf_num'] = inf_num
    result['nan_num'] = nan_num
    result['zero_num'] = zero_num
    result['max_value'] = max_value
    result['min_value'] = min_value
    result['valid_num'] = valid_num
    result['mean'] = mean
    result['median'] = median
    result['std'] = std
    result['med'] = med
    result['skew'] = skew
    result['kurt'] = kurt
    result['mv_max'] = mv_max
    result['mv_min'] = mv_min
    result['med_max'] = med_max
    result['med_min'] = med_min
    result['mv_max_excess'] = mv_max_excess
    result['mv_min_excess'] = mv_min_excess
    result['med_max_excess'] = med_max_excess
    result['med_min_excess'] = med_min_excess
    return result


def cs_skew(arr):
    skew = np.full(arr.shape[:-1], np.nan, dtype=arr.dtype)
    num = (np.isfinite(arr) & (arr != 0)).sum(axis=-1)
    num[np.nanstd(arr, axis=-1, ddof=1) == 0] = 0
    skew[num > 10] = sps.skew(arr[num > 10, :], axis=1, bias=False, nan_policy='omit').data
    return skew


def cs_kurt(arr):
    kurt = np.full(arr.shape[:-1], np.nan, dtype=arr.dtype)
    num = (np.isfinite(arr) & (arr != 0)).sum(axis=-1)
    num[np.nanstd(arr, axis=-1, ddof=1) == 0] = 0
    kurt[num > 10] = sps.kurtosis(arr[num > 10, :], axis=1, fisher=True, bias=False, nan_policy='omit').data
    return kurt


def clip_stats(x, min_clip=-np.inf, max_clip=np.inf):
    mask = (x < min_clip) | (x > max_clip) | ~ np.isfinite(x)
    mean = np.ma.array(x, mask=mask, fill_value=np.nan).mean(axis=-1).data
    std = np.ma.array(x, mask=mask, fill_value=np.nan).std(axis=-1, ddof=1).data
    med = np.ma.median(np.ma.array(x, mask=mask, fill_value=np.nan), axis=-1).data
    mad = np.ma.median(np.ma.array(np.fabs(x - med[..., None]), mask=mask, fill_value=np.nan), axis=-1).data
    sharpe = mean / std
    medmad = med / mad
    return mean, std, sharpe, med, mad, medmad


def d1_mean(x, d):
    return bottleneck.move_mean(x, d)


def d1_sum(x, d):
    return bottleneck.move_sum(x, d)


def d1_delay(x, d):
    return np.pad(x[:-d], (d, 0), mode='constant', constant_values=np.nan)


def d2_delay(x, d):
    return np.pad(x[:-d], ((d, 0), (0, 0)), mode='constant', constant_values=np.nan)


def d1_delta(x, d):
    return x - d1_delay(x, d)


def d1_ema(x, d):
    alpha = (d - 1) / (d + 1)
    weight = alpha ** np.arange(d)
    xf = np.isfinite(x)
    x = np.where(~ xf, np.array([0.]), x)
    cx = np.apply_along_axis(np.convolve, 0, x, weight, 'valid')
    cw = np.apply_along_axis(np.convolve, 0, xf, weight, 'valid')
    return np.pad(cx / cw, (d - 1, 0), mode='constant', constant_values=np.nan)


def roll_pct_wgt_avg(x, y, d):
    x = np.lib.stride_tricks.as_strided(x, shape=(x.shape[0] - d, d + 1), strides=(x.strides[0], x.strides[0])).copy()
    y = np.lib.stride_tricks.as_strided(y, shape=(y.shape[0] - d, d + 1), strides=(y.strides[0], y.strides[0])).copy()
    res = ((x[:, -1:] / x[:, :-1] - 1) * y[:, :-1]).sum(axis=1) / y[:, :-1].sum(axis=1)
    res = np.pad(res, (d, 0), mode='constant', constant_values=np.nan)
    return res



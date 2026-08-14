import bottleneck
import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.stats import norm
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_pre_trade_date

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

def corrcoef(X, y, axis=-1):

    X = X.swapaxes(0, axis)
    X[~ np.isfinite(y)] = np.nan

    X = X - np.nanmean(X, axis=0)
    y = y - np.nanmean(y)
    multi = np.nanmean(X.T * y, axis=1) / (np.nanstd(X, axis=0) * np.nanstd(y))
    multi[np.isinf(multi)] = np.nan
    return multi

def roll_nanmean(arr, window, tolerate=0.1):

    n = bottleneck.move_sum(np.isfinite(arr), window, axis=0)[window - 1:]
    n[n / window <= 1 - tolerate] = np.nan
    x = arr.copy()
    x[~ np.isfinite(arr)] = 0.
    cx = bottleneck.move_sum(x, window, axis=0)[window - 1:]
    cx /= n
    return cx

def roll_nanstd(arr, window, tolerate=0.1):

    n = bottleneck.move_sum(np.isfinite(arr), window, axis=0)[window - 1:]
    n[n / window <= 1 - tolerate] = np.nan
    x = arr.copy()
    x[~ np.isfinite(arr)] = 0.
    cx = bottleneck.move_sum(x, window, axis=0)[window - 1:]
    cx2 = bottleneck.move_sum(x ** 2, window, axis=0)[window - 1:]
    return np.sqrt((cx2 - cx ** 2 / n) / (n - 1))

def roll_nant(arr, window, tolerate=0.1):

    n = bottleneck.move_sum(np.isfinite(arr), window, axis=0)[window - 1:]
    n[n / window <= 1 - tolerate] = np.nan
    x = arr.copy()
    x[~ np.isfinite(arr)] = 0.
    cx = bottleneck.move_sum(x, window, axis=0)[window - 1:]
    cx2 = bottleneck.move_sum(x ** 2, window, axis=0)[window - 1:]
    return cx / np.sqrt((n * cx2 - cx ** 2) / (n - 1))

def roll_nanir(arr, window, tolerate=0.1):

    n = bottleneck.move_sum(np.isfinite(arr), window, axis=0)[window - 1:]
    n[n / window <= 1 - tolerate] = np.nan
    x = arr.copy()
    x[~ np.isfinite(arr)] = 0.
    cx = bottleneck.move_sum(x, window, axis=0)[window - 1:]
    cx2 = bottleneck.move_sum(x ** 2, window, axis=0)[window - 1:]
    return cx / np.sqrt((n * cx2 - cx ** 2) * n / (n - 1))

def roll_windows(a, window):
    """Creates rolling-window 'blocks' of length `window` from `a`.
    Note that the orientation of rows/columns follows that of pandas.
    Example
    -------
    import numpy as np
    onedim = np.arange(20)
    twodim = onedim.reshape((5,4))
    print(twodim)
    [[ 0  1  2  3]
     [ 4  5  6  7]
     [ 8  9 10 11]
     [12 13 14 15]
     [16 17 18 19]]
    print(rwindows(onedim, 3)[:5])
    [[0 1 2]
     [1 2 3]
     [2 3 4]
     [3 4 5]
     [4 5 6]]
    print(rwindows(twodim, 3)[:5])
    [[[ 0  1  2  3]
      [ 4  5  6  7]
      [ 8  9 10 11]]
     [[ 4  5  6  7]
      [ 8  9 10 11]
      [12 13 14 15]]
     [[ 8  9 10 11]
      [12 13 14 15]
      [16 17 18 19]]]
    """

    if window > a.shape[0]:
        raise ValueError(
            "Specified `window` length of {0} exceeds length of"
            " `a`, {1}.".format(window, a.shape[0])
        )
    if isinstance(a, (pd.Series, pd.DataFrame)):
        a = a.values
    if a.ndim == 1:
        a = a.reshape(-1, 1)
    shape = (a.shape[0] - window + 1, window) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    windows = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    if windows.ndim == 1:
        windows = np.atleast_2d(windows)
    return windows

def roll_nanmdd(arr, window):

    arr = arr.copy()
    arr[~ np.isfinite(arr)] = 0.
    np.cumsum(arr, axis=0, out=arr)
    arr = roll_windows(arr, window)
    arr -= np.maximum.accumulate(arr, axis=1)
    arr *= -1
    arr = arr.max(axis=1)
    arr[arr == 0.] = np.nan
    return arr

def factor_direction_merge(arr, pos, neg):

    if arr.shape[0] == 2:
        return np.ma.array(arr[0] * neg + arr[1] * pos, mask=~neg | ~pos, fill_value=np.nan).data
    else:
        return np.ma.array(arr * pos - arr * neg, mask=~neg | ~pos, fill_value=np.nan).data

def factor_strength(pool, metrics, weight, IC_roll, rank_IC_roll, ICIR_roll, rank_ICIR_roll,
                    group_IC_roll, MI_roll, group_MI_roll, active_turn, active_mean, active_std,
                    active_mdd, active_sp_net, active_cm_net, active_mean_net, axis=-1):

    ARR = tuple()
    weight = np.asanyarray(weight) / sum(weight)
    for m in metrics:
        arr = eval(m).astype(float)
        arr[~pool] = np.nan
        arr = arr.swapaxes(0, axis)
        if 'IC' in m:
            arr = np.abs(arr)
        arr_median = np.nanmedian(arr, axis=0)
        arr[pool.swapaxes(0, axis) & ~np.isfinite(arr)] = np.expand_dims(arr_median, axis=0).repeat(
            arr.shape[0], axis=0)[pool.swapaxes(0, axis) & ~np.isfinite(arr)]
        arr = winsorize(arr, axis=0, method='mv', out='raw_rank', alpha=0.01)
        arr_max = np.nanmax(arr, axis=0)
        arr_min = np.nanmin(arr, axis=0) - 1e-7
        arr = (arr - arr_min) / (arr_max - arr_min)
        arr[~pool.swapaxes(0, axis)] = 0.
        ARR += (arr, )
    ARR = np.r_['0,%d' % (pool.ndim + 1), ARR]
    ARR = ARR.transpose(tuple(range(1, ARR.ndim)) + (0,)).dot(weight).swapaxes(0, axis)
    ARR[~pool] = np.nan
    return ARR

def factor_multi_period_strength(pool, metrics, pos, neg, future_days, weight, axis=0):

    weight = np.asanyarray(weight) / sum(weight)
    valid_weight = ~ np.isclose(weight, 0)
    weight = weight[valid_weight]

    metrics = metrics.swapaxes(0, axis)[valid_weight].copy()
    pool = np.all(pool.swapaxes(0, axis)[valid_weight], axis=0)
    pos = np.all(pos.swapaxes(0, axis)[valid_weight], axis=0)
    neg = np.all(neg.swapaxes(0, axis)[valid_weight], axis=0)

    pool &= pos | neg
    metrics[~ np.isfinite(metrics)] = 0.
    metrics = metrics.transpose(tuple(range(1, metrics.ndim)) + (0, )).dot(weight)
    metrics[~pool] = np.nan

    weight = metrics.copy()
    weight[neg] *= -1

    future_days = np.asanyarray(future_days)
    future_days_max = max(future_days[valid_weight])

    return pool, metrics, weight, future_days_max

def factor_corr_filter(pool, corr, metrics, corr_limit):

    corr = np.abs(corr)
    corr[~ np.isfinite(corr)] = 1.
    corr[~ pool] = 0.
    corr.swapaxes(1, 2)[~ pool] = 0.

    rank = (- metrics).argsort(axis=1)
    corr = corr[np.arange(corr.shape[0])[:, None, None], rank[:, :, None], rank[:, None, :]]
    corr_triu = np.tril_indices(corr.shape[1])
    corr[:, corr_triu[0], corr_triu[1]] = 0.

    corr_pool = np.full_like(pool, True)
    corr_pool[np.arange(corr_pool.shape[0])[:, None], rank] = corr.max(axis=2) < corr_limit
    corr_pool &= pool

    return corr_pool

def factor_stats(date_num, future_date_num, factor_num, date_list, select_days, model_days,
                 groups, fee, tolerate, middle_address):

    # summary
    factor_corr = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (middle_address, 'factor_corr', x)) for x in date_list)]
    factor_pool = np.r_['0,2', tuple(np.load('%s%s %s.npy' % (middle_address, 'factor_pool', x)) for x in date_list)]
    factor_turn = np.r_['0,3', tuple(np.load('%s%s %s.npy' % (middle_address, 'factor_turn', x)) for x in date_list)]

    IC = np.full((date_num, future_date_num, factor_num), np.nan)
    rank_IC = np.full((date_num, future_date_num, factor_num), np.nan)
    group_IC = np.full((date_num, future_date_num, factor_num), np.nan)
    MI = np.full((date_num, future_date_num, factor_num), np.nan)
    group_MI = np.full((date_num, future_date_num, factor_num), np.nan)
    group_active = np.full((date_num, factor_num, future_date_num, groups), np.nan)

    for day, date in tqdm(enumerate(date_list)):

        IC[day, :, factor_pool[day]] = np.load('%s%s %s.npy' % (middle_address, 'IC', date))
        rank_IC[day, :, factor_pool[day]] = np.load('%s%s %s.npy' % (middle_address, 'rank_IC', date))
        group_IC[day, :, factor_pool[day]] = np.load('%s%s %s.npy' % (middle_address, 'group_IC', date))
        MI[day, :, factor_pool[day]] = np.load('%s%s %s.npy' % (middle_address, 'MI', date))
        group_MI[day, :, factor_pool[day]] = np.load('%s%s %s.npy' % (middle_address, 'group_MI', date))
        group_active[day, factor_pool[day]] = np.load('%s%s %s.npy' % (middle_address, 'group_active', date))

    # select factor
    factor_pool_select = (bottleneck.move_sum(factor_pool, model_days, axis=0)[select_days-1:] == model_days) & (
        bottleneck.move_sum(factor_pool[:-model_days], select_days - model_days, axis=0)[select_days - model_days-1:] >=
        (select_days - model_days) * (1 - tolerate))

    factor_corr_roll = roll_nanmean(factor_corr, select_days, tolerate=tolerate)
    IC_roll = roll_nanmean(IC, select_days, tolerate=tolerate).transpose(1, 0, 2)
    rank_IC_roll = roll_nanmean(rank_IC, select_days, tolerate=tolerate).transpose(1, 0, 2)
    ICIR_roll = roll_nanir(IC, select_days, tolerate=tolerate).transpose(1, 0, 2) * np.sqrt(244)
    rank_ICIR_roll = roll_nanir(rank_IC, select_days, tolerate=tolerate).transpose(1, 0, 2) * np.sqrt(244)
    group_IC_roll = roll_nanmean(group_IC, select_days, tolerate=tolerate).transpose(1, 0, 2)
    MI_roll = roll_nanmean(MI, select_days, tolerate=tolerate).transpose(1, 0, 2)
    group_MI_roll = roll_nanmean(group_MI, select_days, tolerate=tolerate).transpose(1, 0, 2)

    IC_near = roll_nanmean(IC[select_days - select_days // 2:], select_days // 2, tolerate=tolerate).transpose(1, 0, 2)
    IC_far = roll_nanmean(IC[:select_days // 2 - select_days], select_days // 2, tolerate=tolerate).transpose(1, 0, 2)
    group_IC_near = roll_nanmean(group_IC[select_days - select_days // 2:], select_days // 2, tolerate=tolerate).transpose(1, 0, 2)
    group_IC_far = roll_nanmean(group_IC[:select_days // 2 - select_days], select_days // 2, tolerate=tolerate).transpose(1, 0, 2)

    factor_pos = ((ICIR_roll > 0) & (rank_ICIR_roll > 0) & (IC_near > 0) & (IC_far > 0) & (group_IC_near > 0) &
                  (group_IC_far > 0))
    factor_neg = ((ICIR_roll < 0) & (rank_ICIR_roll < 0) & (IC_near < 0) & (IC_far < 0) & (group_IC_near < 0) &
                  (group_IC_far < 0))

    active_turn = roll_nanmean(factor_turn[:, [0, -1], :], select_days, tolerate=tolerate).transpose(1, 0, 2)
    active_mean = roll_nanmean(group_active[:, :, :, [0, -1]], select_days, tolerate=tolerate).transpose(3, 2, 0, 1)
    active_std = roll_nanstd(group_active[:, :, :, [0, -1]], select_days, tolerate=tolerate).transpose(3, 2, 0, 1)
    active_mdd = roll_nanmdd(group_active[:, :, :, [0, -1]], select_days).transpose(3, 2, 0, 1)

    active_turn = factor_direction_merge(active_turn, factor_pos, factor_neg)
    active_mean = factor_direction_merge(active_mean, factor_pos, factor_neg)
    active_std = factor_direction_merge(active_std, factor_pos, factor_neg)
    active_mdd = factor_direction_merge(active_mdd, factor_pos, factor_neg)


    active_mean_net = active_mean - active_turn * fee
    active_sp_net = active_mean_net / active_std
    active_cm_net = active_mean_net / active_mdd

    return (factor_pool, factor_pool_select, factor_corr_roll, IC_roll, rank_IC_roll, ICIR_roll, rank_ICIR_roll,
            group_IC_roll, MI_roll, group_MI_roll, factor_pos, factor_neg, active_turn, active_mean, active_std,
            active_mdd, active_mean_net, active_sp_net, active_cm_net)

def _factor_select(metrics, metrics_weight, future_days, multi_period_weight, corr_limit, factor_num_limit,
                   factor_proportion_limit, factor_pool_select, factor_corr_roll, factor_pos, factor_neg,
                   active_mean_net, IC_roll, rank_IC_roll, ICIR_roll, rank_ICIR_roll, group_IC_roll, MI_roll,
                   group_MI_roll, active_turn, active_mean, active_std, active_mdd, active_sp_net, active_cm_net):

    factor_pool_select = factor_pool_select & (factor_pos | factor_neg) & (active_mean_net > 0)

    factor_metrics = factor_strength(factor_pool_select, metrics, metrics_weight, IC_roll, rank_IC_roll, ICIR_roll,
                                     rank_ICIR_roll, group_IC_roll, MI_roll, group_MI_roll, active_turn, active_mean,
                                     active_std, active_mdd, active_sp_net, active_cm_net, active_mean_net)

    (factor_multi_period_pool, factor_multi_period_metrics, factor_multi_period_weight, future_days_max
     ) = factor_multi_period_strength(
        factor_pool_select, factor_metrics, factor_pos, factor_neg, future_days, multi_period_weight)

    corr_pool = factor_corr_filter(factor_multi_period_pool, factor_corr_roll, factor_multi_period_metrics, corr_limit)
    select_num = corr_pool.sum(axis=1)
    factor_multi_period_metrics[~ corr_pool] = np.nan
    select_rank = bottleneck.nanrankdata(- factor_multi_period_metrics, axis=1)
    double_select = ((select_rank.T <= factor_num_limit) & (select_rank.T <= select_num * factor_proportion_limit)).T
    select_rank[~ double_select] = np.nan
    factor_multi_period_weight[~ double_select] = 0
    factor_multi_period_weight = (factor_multi_period_weight.T / np.nansum(np.abs(factor_multi_period_weight), axis=1)).T
    return factor_multi_period_weight, select_rank, future_days_max


def simple_weighted_factor(compound_name, start_date, select_days, factor_num, future_days_max, end_date, code_num,
                           factor_pool, date_list, code_list, factor_multi_period_weight, middle_address,
                           compound_address):

    model_date_list = get_date_range(get_pre_trade_date(start_date, - select_days - future_days_max), end_date)
    compound_factor = np.empty((len(model_date_list), code_num))
    for date in tqdm(model_date_list):
        factor_pool_day = factor_pool[date_list.index(date)]
        factor_multi_period_weight_day = factor_multi_period_weight[date_list.index(date) - select_days - future_days_max]
        factor = np.full((factor_num, code_num), 0.)
        factor[factor_pool_day] = np.load('%s%s %s.npy' % (middle_address, 'factor_standardize', date))
        compound_factor[model_date_list.index(date)] = factor_multi_period_weight_day.dot(factor)
    compound_factor = pd.DataFrame(compound_factor, index=model_date_list, columns=code_list)
    compound_factor.to_hdf('%s%s' % (compound_address, compound_name), compound_name, format='t')

def factor_select(start_date, end_date, select_days, model_days, future_days, groups, metrics, metrics_weight,
                  multi_period_weight, corr_limit, factor_num_limit, factor_proportion_limit, fee, tolerate,
                  middle_address, factor_list, compound_name, compound_address):

    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240, no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120, no_limit_up=False, no_limit_down=False,
                                  other_limit={'mkt_cap_ard': 0.05}, start_date=start_date, end_date=end_date)

    date_list = stock_pool.index.to_list()
    code_list = stock_pool.columns.to_list()

    if isinstance(future_days, int):
        future_days = list(range(1, future_days + 1))
    elif not isinstance(future_days, list):
        raise TypeError('future_days must be int or list')
    future_date_num = len(future_days)

    factor_num = len(factor_list)
    date_num = len(date_list)
    code_num = len(code_list)

    (factor_pool, factor_pool_select, factor_corr_roll, IC_roll, rank_IC_roll, ICIR_roll, rank_ICIR_roll,
     group_IC_roll, MI_roll, group_MI_roll, factor_pos, factor_neg, active_turn, active_mean, active_std,
     active_mdd, active_mean_net, active_sp_net, active_cm_net) = factor_stats(
        date_num, future_date_num, factor_num, date_list, select_days, model_days, groups, fee, tolerate, middle_address)


    factor_multi_period_weight, select_rank, future_days_max = _factor_select(
        metrics, metrics_weight, future_days, multi_period_weight, corr_limit, factor_num_limit,
        factor_proportion_limit, factor_pool_select, factor_corr_roll, factor_pos, factor_neg,
        active_mean_net, IC_roll, rank_IC_roll, ICIR_roll, rank_ICIR_roll, group_IC_roll, MI_roll,
        group_MI_roll, active_turn, active_mean, active_std, active_mdd, active_sp_net, active_cm_net)

    simple_weighted_factor(compound_name, start_date, select_days, factor_num, future_days_max, end_date, code_num,
                           factor_pool, date_list, code_list, factor_multi_period_weight, middle_address,
                           compound_address)

    return factor_pool, factor_multi_period_weight, select_rank

if __name__ == '__main__':

    middle_address = '/data/user/015836/model/temp20200513/'
    compound_address = '/data/user/015836/model/compound/'

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

    start_date = 20140102
    end_date = 20181228

    future_days = 5

    groups = 10

    fee = 0.002

    select_days = 120
    model_days = 60

    tolerate = 0.2
    corr_limit = 0.7

    metrics = ['active_mean_net', 'active_sp_net']
    metrics_weight = [1, 1]
    multi_period_weight = [0, 0, 0, 0, 1]

    factor_num_limit = np.inf
    factor_proportion_limit = 1.

    compound_name = 'compound'

    factor_pool, factor_multi_period_weight, select_rank = factor_select(
        start_date, end_date, select_days, model_days, future_days, groups, metrics, metrics_weight,
        multi_period_weight, corr_limit, factor_num_limit, factor_proportion_limit, fee, tolerate,
        middle_address, factor_list, compound_name, compound_address)
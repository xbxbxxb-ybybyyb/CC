import numpy as np
import pandas as pd
import os
import IO

start_date = 20160101
end_date = 20191231
path2_factor = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/20241017TTick_combination/'

label_df = IO.read_data([start_date, end_date], alt='/data/group/800463/data/project1_public/factor_lib_v3/sft_update_europa_filter_20160101_20191231.h5')
def filter_label(df):
    time_interval = [93000000, 143000000]
    last_is_zt = False
    first_is_zt = False
    open_is_zt = False
    Flag_SH_SZ = None
    last_buy_rise = 0.025,
    low_open = -0.05
    after_not_ul_len = 10
    low_price = 2,
    df['first_is_zt'] = (df['high_price'] >= (df['trigger_price']))
    time_interval_filter = (df['ZT_Time'] >= time_interval[0]) & (df['ZT_Time'] <= time_interval[1])
    open_is_zt_filter = df['open_is_zt'] == open_is_zt
    low_open_filter = df['T_o2pre'] >= low_open
    after_not_ul_len_filter = df['after_not_ul_len'] > after_not_ul_len
    low_price_filter = df['pre_close'] >= low_price
    first_is_zt_filter = df['first_is_zt'] == first_is_zt
    last_is_zt_filter = df['last_is_zt'] == int(last_is_zt) if last_is_zt is not None else (
                df['last_is_zt'] == df['last_is_zt'])
    last_buy_rise_filter = df['last_buy_rise'] <= last_buy_rise
    sh_sz_filter = df['Flag_SH_SZ'] == int(Flag_SH_SZ) if Flag_SH_SZ is not None else (
                df['Flag_SH_SZ'] == df['Flag_SH_SZ'])
    all_filter = time_interval_filter & open_is_zt_filter & low_open_filter & after_not_ul_len_filter & low_price_filter \
                 & first_is_zt_filter & last_is_zt_filter & last_buy_rise_filter & sh_sz_filter
    df = df[all_filter]
    return df
# label_df = filter_label(label_df)
label_df = label_df[~label_df['value'].isna()]

def _mul_10(x1):
    with np.errstate(over='ignore', under='ignore'):
        return np.array(x1 * 10)
def _div_2(x1):
    with np.errstate(over='ignore', under='ignore'):
        return x1 / 2
def _square(x1):
    with np.errstate(over='ignore', under='ignore'):
        return x1 * x1

def _weighted_pearson(y, y_pred, w):
    """Calculate the weighted Pearson correlation coefficient."""
    with np.errstate(divide='ignore', invalid='ignore'):
        y_pred_demean = y_pred - np.average(y_pred, weights=w)
        y_demean = y - np.average(y, weights=w)
        corr = ((np.sum(w * y_pred_demean * y_demean) / np.sum(w)) /
                np.sqrt((np.sum(w * y_pred_demean ** 2) *
                         np.sum(w * y_demean ** 2)) /
                        (np.sum(w) ** 2)))
    if np.isfinite(corr):
        return np.abs(corr)
    return 0.
def rankdata(a, method='average'):
    if method not in ('average', 'min', 'max', 'dense', 'ordinal'):
        raise ValueError('unknown method "{0}"'.format(method))
    arr = np.ravel(np.asarray(a))
    algo = 'mergesort' if method == 'ordinal' else 'quicksort'
    sorter = np.argsort(arr, kind=algo)
    inv = np.empty(sorter.size, dtype=np.intp)
    inv[sorter] = np.arange(sorter.size, dtype=np.intp)
    if method == 'ordinal':
        return inv + 1
    arr = arr[sorter]
    obs = np.r_[True, arr[1:] != arr[:-1]]
    dense = obs.cumsum()[inv]
    if method == 'dense':
        return dense
    # cumulative counts of each unique value
    count = np.r_[np.nonzero(obs)[0], len(obs)]
    if method == 'max':
        return count[dense]
    if method == 'min':
        return count[dense - 1] + 1
    # average method
    return .5 * (count[dense] + count[dense - 1] + 1)
def _weighted_spearman(y, y_pred, w):
    """Calculate the weighted Spearman correlation coefficient."""
    y_pred_ranked = np.apply_along_axis(rankdata, 0, y_pred)
    y_ranked = np.apply_along_axis(rankdata, 0, y)
    return _weighted_pearson(y_pred_ranked, y_ranked, w)

label_df_ = label_df.copy().rank(axis=0)
def metric_corr_ic_(y,y_pred,w):
    if len(y_pred) == len(label_df_):
        label_df_['test'] = y_pred
        corr = abs(label_df_.drop(['test'], axis=1).corrwith(label_df_['test'].rank(axis=0))).max()
    else:
        print('error, length dont match')
        return 0
    res = _weighted_spearman(y, y_pred, w) # IC
    if np.isnan(res) or np.isnan(corr):
        return 0
    if corr <= 0.65:
        return res
    elif res >= 0.07:
        return res * (1.5-abs(corr))
    else:
        return res * (1.5-abs(corr)) * 0.8
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 18:06:04 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from joblib import Parallel, delayed



def ts_rank(data, d = 1200):
    # moving time-series rank for the past d periods
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), 'input must be a series, dataframe or ndarray'
    if d == 1:
        output = data
    else:
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
        elif isinstance(data, np.ndarray):
            output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
    return output


def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame) or isinstance(sig, np.ndarray), 'input must be a series, dataframe or ndarray'
    if window == 0:
        return sig
    else:
        if method == 'max_min':
            if isinstance(sig, pd.DataFrame):
                sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, columns=sig.columns)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, pd.Series):
                sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
                sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                    index=sig.index, name=sig.name)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            elif isinstance(sig, np.ndarray):
                sig_max = bk.move_max(sig, window=window, min_count=int(window / 2), axis=0)
                sig_min = bk.move_min(sig, window=window, min_count=int(window / 2), axis=0)
                temp = sig_max - sig_min
                temp[abs(temp)<1e-8] = np.nan
                signal = (sig - sig_min) / temp
            return 2 * signal - 1
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            elif isinstance(sig, np.ndarray):
                signal = bk.move_rank(sig, window=window, min_count=int(window/ 2), axis=0)
            return signal

def rolling_linear_reg(x, y, window_size):
    x2=np.power(x,2)
    xy=x*y
    window = np.ones(int(window_size))
    a1=np.convolve(xy, window, 'full')*window_size
    a2=np.convolve(x, window, 'full')*np.convolve(y, window, 'full')
    b1=np.convolve(x2, window, 'full')*window_size
    b2=np.power(np.convolve(x, window, 'full'),2)
    alphas=(a1-a2)/(b1-b2)
    betas=(np.convolve(y, window, 'full')-alphas*np.convolve(x, window, 'full'))/float(window_size)
    alphas=alphas[:-1*(window_size-1)] #numpy array of rolled alpha
    betas=betas[:-1*(window_size-1)] 
    alphas[:window_size-1] = np.nan
    return alphas

def ts_std(df1, d):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output

def to_ts(df, ret, LS = True, Lag = False):
    if LS == True:
        if Lag == False:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
        else:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)
    else:
        if Lag == False:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
        else:
            return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)

def decay_linear(x1, window):
    interval = x1.shape[1]
    num = np.array(list(range(window))) + 1.0
    coe = np.tile(num, (x1.shape[0],1))
    def _sub_decay_linear(k, coe):
        data = x1[:, k:window + k]
        isnan = np.isnan(data)
        coe[isnan] = np.nan
        sum_days = np.nansum(coe,axis = 1)
        sum_days = np.tile(sum_days,(window,1)).T
        coe = coe/sum_days
        decay = np.nansum(coe*data,axis = 1)
        decay[isnan[:,-1]] = np.nan
        return decay
    tmparray = np.array(Parallel(n_jobs=-1)(delayed(_sub_decay_linear)(k + 1, coe) for k in range (0, interval-window))).T
    result = np.full([x1.shape[0], window],np.nan)
    result = np.column_stack([result,tmparray])
    return result

def calc_change_helper(score_raw,short_win,long_win,ts_pct_win,sign=1,min_pct=0.9):
    #score_change_raw = sign*(score_raw.rolling(short_win,int(min_pct*short_win)).mean() - score_raw.rolling(long_win,int(min_pct*long_win)).mean())
    score_change_raw = sign*(bk.move_mean(score_raw, short_win, min_count = int(min_pct*short_win), axis = 0) - bk.move_mean(score_raw, long_win, min_count = int(min_pct*long_win), axis = 0))
    score_change = calc_ts_pct(score_change_raw,ts_pct_win)
    
    return score_change

def calc_ts_pct(ts,ts_pct_win=20,min_pct=0.9,force_range=False):
    min_win = int(min_pct*ts_pct_win)
    ts_pct_np = bk.move_rank(ts,ts_pct_win,min_win,axis=0)
    if force_range:
        ts_pct_np = (ts_pct_np + 1)/2

    return ts_pct_np

def calc_std_helper(score_raw,std_win,ts_pct_win,min_pct=0.9, norm = False):
    score_std_raw = bk.move_std(score_raw, std_win, min_count = int(min_pct*std_win), axis = 0)
    if norm == True:
        score_std = calc_ts_pct(score_std_raw,ts_pct_win)
    else: 
        score_std = score_std_raw
    return score_std

def calc_ma_helper(score_raw,ma_win,ts_pct_win,min_pct=0.9, norm = False):
    score_ma_raw = bk.move_mean(score_raw, ma_win, min_count = int(min_pct*ma_win), axis = 0)
    if norm == True:
        score_ma = calc_ts_pct(score_ma_raw,ts_pct_win)
    else:
        score_ma = score_ma_raw
    return score_ma

def REF(x, n):
    res = x[:-n]
    return res

def MA(x, n):
    res = bk.move_mean(x, n, min_count = 1, axis = 0)
    return res

def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    # 这是后面算子计算的辅助函数
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table

    
def get_top_mean(df1, d):
    output = pd.Series(np.nan, index=df1.index)
    a = rolling_window(df1, d)
    b = np.sort(a)
    c = np.nanmean(b[:,-5:], axis=1)
    flag = np.sum(np.isnan(a), axis=1) 
    flag = np.where(flag <= d - int(d / 2), 1, np.nan)
    output.iloc[d - 1:] = c * flag
    return output


def multi_processing_joblib(df, func, n_jobs, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T

def r(data, x=np.nan):

    data[abs(data) < 1e-8] = x
    return data

def cross(df):
    df[~np.isfinite(abs(df))] = np.nan
    if (isinstance(df, np.ndarray)):
        
        if len(np.shape(df)) != 1:
            a = df   
            b = (np.nansum((a == 0), axis = 1)>350)
            a[b == True] = np.nan
            a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
        else:
            a = df
            b = (np.nansum((a == 0))>350)
            if b == True:
                a = np.nan
            else:
                a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))
    else:
        a = df.copy().values
        if (isinstance(df, pd.DataFrame)):
            b = (np.nansum((a == 0), axis = 1)>350)
            a[b == True] = np.nan
            a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])

        else:
            b = (np.nansum((a == 0))>350)
            if b == True:
                a = np.nan
            else:
                a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))

  
    return a

def cross2(df):
    df_temp = df.copy()
    df_temp[df_temp == 0] = np.nan
    return df_temp

def cross3(df):
    if (isinstance(df, pd.DataFrame)):
        df_temp = df.copy()
        a = ((df_temp == 0).sum()>300)
        df_temp.loc[a == True] = np.nan
        df_temp = cross2(df_temp)
    else:
        df_temp = df.copy()
        if ((df_temp == 0).sum()>300):
            df_temp = np.nan
        else:
            df_temp = cross2(df_temp)

    return df_temp


def cross4(df):
    if (isinstance(df, np.ndarray)):
        if len(np.shape(df)) != 1:
            a = df   
            b = (np.nansum((a == 0), axis = 1)>300)
            a[b == True] = np.nan
            a[a==0] = np.nan 
            #a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
        else:
            a = df
            b = (np.nansum((a == 0))>300)
            if b == True:
                a[:] = np.nan
            #else:
                #a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))
    else:
        a = df.copy().values
        if (isinstance(df, pd.DataFrame)):
            b = (np.nansum((a == 0), axis = 1)>300)
            a[b == True] = np.nan
            #a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
            a[a==0] = np.nan 
        else:
            b = (np.nansum((a == 0))>300)
            if b == True:
                a[:] = np.nan
            #else:
                #a = np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99))

        
    return a




def cross_if(df):
    df[~np.isfinite(abs(df))] = np.nan
    if (isinstance(df, np.ndarray)):
        
        if len(np.shape(df)) != 1:
            a = df   
            b = (np.nansum((a == 0), axis = 1)>200)
            a[b == True] = np.nan
            a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
        else:
            a = df
            b = (np.nansum((a == 0))>200)
            if b == True:
                a = np.nan
            else:
                a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))
    else:
        a = df.copy().values
        if (isinstance(df, pd.DataFrame)):
            b = (np.nansum((a == 0), axis = 1)>200)
            a[b == True] = np.nan
            a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])

        else:
            b = (np.nansum((a == 0))>200)
            if b == True:
                a = np.nan
            else:
                a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))

  
    return a



def cross4_if(df):
    if (isinstance(df, np.ndarray)):
        if len(np.shape(df)) != 1:
            a = df   
            b = (np.nansum((a == 0), axis = 1)>120)
            a[b == True] = np.nan
            a[a==0] = np.nan 
            #a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
        else:
            a = df
            b = (np.nansum((a == 0))>120)
            if b == True:
                a[:] = np.nan
            #else:
                #a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))
    else:
        a = df.copy().values
        if (isinstance(df, pd.DataFrame)):
            b = (np.nansum((a == 0), axis = 1)>120)
            a[b == True] = np.nan
            #a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
            a[a==0] = np.nan 
        else:
            b = (np.nansum((a == 0))>120)
            if b == True:
                a[:] = np.nan
            #else:
                #a = np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99))

        
    return a
##########
import pandas as pd
import numpy as np
import bottleneck as bk
import scipy.stats
from help_functions_wsc import rolling_window, rolling_window_upgrade, replace_zero
import warnings

warnings.filterwarnings('ignore')

__all__ = ['add2', 'div2', 'inv1', 'log', 'mul2', 'max2', 'min2', 'neg1', 'pairwise_corr_np', 'rolling_norm',
           'section_rank_np', 'sqrt', 'square', 'sub2', 'ts_argmax', 'ts_argmin', 'ts_corr', 'ts_cov',
           'ts_decay_linear', 'ts_delay', 'ts_delta', 'ts_ema', 'ts_ema_span', 'ts_max', 'ts_mean', 'ts_median',
           'ts_min', 'ts_pct_change', 'ts_pred', 'ts_pred_delta', 'ts_rank', 'ts_reg_alpha', 'ts_reg_beta',
           'ts_reg_residual', 'ts_skew', 'ts_std', 'ts_sum', 'ts_truncated_ema', 'ts_truncated_ema_span']


def add2(x1, x2):
    return np.add(x1, x2)


def div2(x1, x2):
    x2 = replace_zero(x2)
    return np.divide(x1, x2)


def inv1(df1):
    df1 = replace_zero(df1)
    return 1 / df1


def log(data):
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    data = replace_zero(data)
    output = np.log(data)
    return output


def mul2(x1, x2):
    return np.multiply(x1, x2)


def max2(x1, x2):
    return np.maximum(x1, x2)


def min2(x1, x2):
    return np.minimum(x1, x2)


def neg1(x):
    return -x


def pairwise_corr_np(data1, data2, axis=0):
    # 对两个相同shape的np.ndarray，计算对应行/列的相关性
    if not (isinstance(data1, np.ndarray) & isinstance(data2, np.ndarray)):
        raise TypeError('Only supports the following type: np.ndarray')
    if data1.shape != data2.shape:
        raise ValueError('`data1` and `data2` must be the same shape.')
    if data1.ndim not in [1, 2]:
        raise ValueError('`data1` and `data2` must be a 1D or 2D array')
    if data1.ndim == 1:
        return np.ma.corrcoef(np.ma.masked_invalid(data1), np.ma.masked_invalid(data2)).data[0, 1]
    else:
        flag = np.isnan(data1) | np.isnan(data2)
        data1[flag] = np.nan
        data2[flag] = np.nan
        if axis == 1:
            data1_centralized = data1 - np.nanmean(data1, axis=1, keepdims=True)
            data2_centralized = data2 - np.nanmean(data2, axis=1, keepdims=True)
            return np.nansum(data1_centralized * data2_centralized, axis=1) / np.sqrt(
                np.nansum(data1_centralized ** 2, axis=1) * np.nansum(data2_centralized ** 2, axis=1))
        elif axis == 0:
            data1_centralized = data1 - np.nanmean(data1, axis=0)
            data2_centralized = data2 - np.nanmean(data2, axis=0)
            return np.nansum(data1_centralized * data2_centralized, axis=0) / np.sqrt(
                np.nansum(data1_centralized ** 2, axis=0) * np.nansum(data2_centralized ** 2, axis=0))


def rolling_norm(data, window=1200):
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if window == 1:
        return data
    else:
        if isinstance(data, pd.DataFrame):
            data_max = pd.DataFrame(bk.move_max(data, window=window, min_count=int(window / 2), axis=0),
                                    index=data.index, columns=data.columns)
            data_min = pd.DataFrame(bk.move_min(data, window=window, min_count=int(window / 2), axis=0),
                                    index=data.index, columns=data.columns)
            temp = data_max - data_min
            temp[abs(temp) < 1e-8] = np.nan
            data = (data - data_min) / temp
        elif isinstance(data, pd.Series):
            data_max = pd.Series(bk.move_max(data, window=window, min_count=int(window / 2), axis=0),
                                 index=data.index, name=data.name)
            data_min = pd.Series(bk.move_min(data, window=window, min_count=int(window / 2), axis=0),
                                 index=data.index, name=data.name)
            temp = data_max - data_min
            temp[abs(temp) < 1e-8] = np.nan
            data = (data - data_min) / temp
        elif isinstance(data, np.ndarray):
            data_max = bk.move_max(data, window=window, min_count=int(window / 2), axis=0)
            data_min = bk.move_min(data, window=window, min_count=int(window / 2), axis=0)
            temp = data_max - data_min
            temp[abs(temp) < 1e-8] = np.nan
            data = (data - data_min) / temp
        return 2 * data - 1


# def section_rank_np(data, pct=False):
#     # 基于numpy的截面排序，对应df.rank(method='first')
#     if not isinstance(data, np.ndarray):
#         raise TypeError('Only supports the following type: np.ndarray')
#     data_argsort = data.argsort().argsort() + 1.  # +1是因为numpy从0计数，pandas从1计数
#     data_argsort[np.isnan(data)] = np.nan  # numpy argsort会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
#     if pct == True:
#         data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
#     return data_argsort
def section_rank_np(data, pct=False):
    # 基于numpy的截面排序，对应df.rank(method='first')
    if not isinstance(data, np.ndarray):
        raise TypeError('Only supports the following type: np.ndarray')
    data_argsort = bk.rankdata(data, axis=1)
    data_argsort[np.isnan(data)] = np.nan  # bottleneck rankdata会让nan也参与排序，但是pandas不会，所以把这些值重新置为nan
    if pct == True:
        data_argsort = data_argsort / (~np.isnan(data)).sum(axis=1, keepdims=True)
    return data_argsort


def shift_np(arr, num, fill_value=np.nan):
    # shift function for numpy
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result[:] = arr
    return result


def sqrt(data):
    # square root operation
    output = np.sqrt(data)
    return output


def square(data):
    # x**2
    output = data ** 2
    return output



def sub2(x1, x2):
    return np.subtract(x1, x2)


def ts_argmax(data, d):
    # which moment ts_max(x, d) occurred on.
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    elif isinstance(data, np.ndarray):
        output = bk.move_argmax(data, window=d, min_count=int(d / 2), axis=0)
    return (d - 1) - output


def ts_argmin(data, d):
    # which moment ts_min(x, d) occurred on.
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    elif isinstance(data, np.ndarray):
        output = bk.move_argmin(data, window=d, min_count=int(d / 2), axis=0)
    return (d - 1) - output


def ts_corr(data1, data2, d):
    # data1, data2过去d条数据的时序相关系数
    if type(data1) != type(data2):
        raise TypeError('`data1` and `data2` must be the same type.')
    if data1.shape != data2.shape:
        raise ValueError('`data1` and `data2` must be the same shape.')
    if not (isinstance(data1, pd.Series) or isinstance(data1, pd.DataFrame) or isinstance(data1, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data1, np.ndarray):
        output = np.full(data1.shape, np.nan)
        data1_expanding = rolling_window_upgrade(data1, d)
        data2_expanding = rolling_window_upgrade(data2, d)
        flag = np.isnan(data1_expanding) | np.isnan(data2_expanding)
        flag1 = np.sum(flag, axis=-1)  # 缺失值个数
        flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
        data1_expanding[flag] = np.nan
        data2_expanding[flag] = np.nan
        data1_expanding_centralized = data1_expanding - np.nanmean(data1_expanding, axis=-1, keepdims=True)
        data2_expanding_centralized = data2_expanding - np.nanmean(data2_expanding, axis=-1, keepdims=True)
        output[d - 1:] = np.nansum(data1_expanding_centralized * data2_expanding_centralized, axis=-1) / np.sqrt(
            np.nansum(data1_expanding_centralized ** 2, axis=-1) * np.nansum(data2_expanding_centralized ** 2,
                                                                             axis=-1)) * flag2
    else:
        output = data1.rolling(d, min_periods=int(d / 2)).corr(data2)
        output.iloc[:d - 1] = np.nan
    return output


def ts_cov(data1, data2, d):
    # data1, data2过去d条数据的时序协方差
    if type(data1) != type(data2):
        raise TypeError('`data1` and `data2` must be the same type.')
    if data1.shape != data2.shape:
        raise ValueError('`data1` and `data2` must be the same shape.')
    if not (isinstance(data1, pd.Series) or isinstance(data1, pd.DataFrame) or isinstance(data1, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data1, np.ndarray):
        output = np.full(data1.shape, np.nan)
        data1_expanding = rolling_window_upgrade(data1, d)
        data2_expanding = rolling_window_upgrade(data2, d)
        flag = np.isnan(data1_expanding) | np.isnan(data2_expanding)
        flag1 = np.sum(flag, axis=-1)  # 缺失值个数
        flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
        data1_expanding[flag] = np.nan
        data2_expanding[flag] = np.nan
        data1_expanding_centralized = data1_expanding - np.nanmean(data1_expanding, axis=-1, keepdims=True)
        data2_expanding_centralized = data2_expanding - np.nanmean(data2_expanding, axis=-1, keepdims=True)
        output[d - 1:] = np.nansum(data1_expanding_centralized*data2_expanding_centralized, axis=-1) * flag2 / (
                d - 1 - flag1)
    else:
        output = data1.rolling(d, min_periods=int(d / 2)).cov(data2)
        output.iloc[:d - 1] = np.nan
    return output


def ts_decay_linear(data, d, weight=None):
    # weighted moving average over the past d periods
    # default weight: linearly decaying weights d, d – 1, …, 1 (rescaled to sum up to 1)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if data.ndim not in [1, 2]:
        raise ValueError('`data` must be a 1D or 2D array')
    if weight is None:
        weight = np.arange(d) + 1.0
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    if data.ndim == 2:
        weight_expanding = np.tile(weight, (data_expanding.shape[0], data_expanding.shape[1], 1))
    elif data.ndim == 1:
        weight_expanding = np.tile(weight, (data_expanding.shape[0], 1))
    flag = np.isnan(data_expanding) | np.isnan(weight_expanding)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    data_expanding[flag] = np.nan
    weight_expanding[flag] = np.nan
    output_need = (np.nansum(data_expanding * weight_expanding, axis=-1) / np.nansum(weight_expanding, axis=-1)) * flag2
    if isinstance(data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d - 1:] = output_need
    elif isinstance(data, pd.Series):
        output = pd.Series(np.nan, index=data.index, name=data.name)
        output.iloc[d - 1:] = output_need
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(np.nan, index=data.index, columns=data.columns)
        output.iloc[d - 1:] = output_need
    return output


def ts_delay(data, d):
    # A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = np.empty_like(data)
        if d >= 0:
            output[d:] = data[:-d]
            output[:d] = np.nan
        else:
            output[:d] = data[-d:]
            output[d:] = np.nan

    else:
        output = data.shift(periods=d)
    return output


def ts_delta(data, d):
    # A_i - A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = data - ts_delay(data, d)
    else:
        output = data.diff(periods=d)
    return output


def ts_ema(df1, d):
    output = df1.ewm(alpha=d, adjust=False).mean()
    return output


def ts_ema_span(df1, d):
    output = df1.ewm(span=d, adjust=False).mean()
    return output


def ts_max(data, d):
    # moving time-series max for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_max(data, window=d, min_count=int(d / 2), axis=0)
        elif isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_max(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_max(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_mean(data, d):
    # moving time-series mean for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_mean(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_median(data, d):
    # moving time-series meidan for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = bk.move_median(data, window=d, min_count=int(d / 2), axis=0)
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_median(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_median(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    return output


def ts_min(data, d):
    # moving time-series minimum for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = bk.move_min(data, window=d, min_count=int(d / 2), axis=0)
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_min(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    return output


def ts_pct_change(data, d=1):
    # (A_n - A_(n-d)) / A_(n-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance (data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d:] = ((data[d:]-data[:-d]) / replace_zero(data[:-d]))
    else:
        output = data.pct_change(d, fill_method=None)
    return output


def ts_pred(data, d, reg_x=None):
    """
    use rolling linear regression to predict value
    :param data: dataframe, series or ndarray
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like, one dimension
        regressor
    :return: dataframe or series
        the predicted value of rolling linear regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    reg_beta = ts_reg_beta(data, d, reg_x)
    reg_alpha = ts_reg_alpha(data, d, reg_x)
    reg_pred = ts_delay((reg_beta * (d + 1) + reg_alpha), 1)
    return reg_pred


def ts_pred_delta(data, d, reg_x=None):
    """
    the difference of the predicted value of rolling linear regression and real value
    :param data: dataframe, series or ndarray
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like, one dimension
        regressor
    :return: dataframe, series or ndarray
        the difference of the predicted value of rolling linear regression and real value
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    reg_beta = ts_reg_beta(data, d, reg_x)
    reg_alpha = ts_reg_alpha(data, d, reg_x)
    reg_pred = ts_delay((reg_beta * (d + 1) + reg_alpha), 1)
    reg_delta = data - reg_pred
    return reg_delta


def ts_rank(data, d):
    # moving time-series rank for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
        elif isinstance(data, np.ndarray):
            output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
    return output


def ts_reg_alpha(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到截距项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        intercept term of regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if data.ndim not in [1, 2]:
        raise ValueError('`data` must be a 1D or 2D array')
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
        if data.ndim == 2:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], data_expanding.shape[1], 1))
        elif data.ndim == 1:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], 1))
    else:
        if len(reg_x) not in [data.shape[0], d]:
            raise ValueError('the length of `reg_x` must equals the length of data or d.')
        elif len(reg_x) == d:
            if data.ndim == 2:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], data_expanding.shape[1], 1))
            elif data.ndim == 1:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], 1))
        elif len(reg_x) == data.shape[0]:
            reg_x_expanding = rolling_window_upgrade(reg_x, d)

    flag = np.isnan(data_expanding) | np.isnan(reg_x_expanding)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    data_expanding[flag] = np.nan
    reg_x_expanding[flag] = np.nan
    data_expanding_centralized = data_expanding - np.nanmean(data_expanding, axis=-1, keepdims=True)
    reg_x_expanding_centralized = reg_x_expanding - np.nanmean(reg_x_expanding, axis=-1, keepdims=True)
    reg_beta = np.nansum(data_expanding_centralized * reg_x_expanding_centralized, axis=-1) / np.nansum(
        reg_x_expanding_centralized ** 2, axis=-1)
    output_need = (np.nanmean(data_expanding, axis=-1) - reg_beta * np.nanmean(reg_x_expanding, axis=-1)) * flag2
    if isinstance(data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d - 1:] = output_need
    elif isinstance(data, pd.Series):
        output = pd.Series(np.nan, index=data.index, name=data.name)
        output.iloc[d - 1:] = output_need
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(np.nan, index=data.index, columns=data.columns)
        output.iloc[d - 1:] = output_need
    return output


def ts_reg_beta(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到斜率项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        slope term of regression
    """
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if data.ndim not in [1, 2]:
        raise ValueError('`data` must be a 1D or 2D array')
    try:
        data_expanding = rolling_window_upgrade(data.values, d)
    except AttributeError:
        data_expanding = rolling_window_upgrade(data, d)
    if reg_x is None:
        reg_x1 = np.arange(d) + 1.0
        if data.ndim == 2:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], data_expanding.shape[1], 1))
        elif data.ndim == 1:
            reg_x_expanding = np.tile(reg_x1, (data_expanding.shape[0], 1))
    else:
        if len(reg_x) not in [data.shape[0], d]:
            raise ValueError('the length of `reg_x` must equals the length of data or d.')
        elif len(reg_x) == d:
            if data.ndim == 2:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], data_expanding.shape[1], 1))
            elif data.ndim == 1:
                reg_x_expanding = np.tile(reg_x, (data_expanding.shape[0], 1))
        elif len(reg_x) == data.shape[0]:
            reg_x_expanding = rolling_window_upgrade(reg_x, d)

    flag = np.isnan(data_expanding) | np.isnan(reg_x_expanding)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    data_expanding[flag] = np.nan
    reg_x_expanding[flag] = np.nan
    data_expanding_centralized = data_expanding - np.nanmean(data_expanding, axis=-1, keepdims=True)
    reg_x_expanding_centralized = reg_x_expanding - np.nanmean(reg_x_expanding, axis=-1, keepdims=True)   
    output_need = np.nansum(data_expanding_centralized * reg_x_expanding_centralized, axis=-1) / np.nansum(
        reg_x_expanding_centralized ** 2, axis=-1) * flag2
    if isinstance(data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d - 1:] = output_need
    elif isinstance(data, pd.Series):
        output = pd.Series(np.nan, index=data.index, name=data.name)
        output.iloc[d - 1:] = output_need
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(np.nan, index=data.index, columns=data.columns)
        output.iloc[d - 1:] = output_need
    return output


def ts_reg_residual(data, d, reg_x=None):
    """
    过去d期A对reg_x或者1:d滚动回归得到的残差项
    :param data: array_like
        regressand
    :param d: int
        rolling interval
    :param reg_x: array_like or None
        regressor
    :return: array_like
        residual term of regression
    """
    if reg_x is None:  # or (len(reg_x) == d):
        reg_x_expanding = np.full_like(data, d)
    elif len(reg_x) == d:
        reg_x_expanding = np.full_like(data, reg_x[-1])
    elif len(reg_x) == data.shape[0]:
        reg_x_expanding = reg_x
    reg_slope = ts_reg_beta(data, d, reg_x)
    reg_intercept = ts_reg_alpha(data, d, reg_x)
    output = data - reg_slope * reg_x_expanding - reg_intercept
    return output


def ts_skew(data, d):
    # moving time-series skew over the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = np.full_like(data, np.nan)
            temp = rolling_window_upgrade(data, d)
            output[d - 1:] = scipy.stats.skew(temp, axis=-1, bias=False)
        else:
            output = df1.rolling(d, min_periods=int(d / 2)).skew()
            output.iloc[:d - 1] = np.nan
    return output


def ts_std(data, d):
    # moving time-series rank for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=data.index, name=data.name)
    return output


def ts_sum(data, d):
    # moving time-series sum for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_sum(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_sum(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_sum(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_truncated_ema(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = np.append(alpha * np.array([(1 - alpha) ** i for i in range(d - 1)]), (1 - alpha) ** (d - 1))[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span(data, d, span):
    # truncated ema
    return ts_truncated_ema(data=data, d=d, alpha=2 / (span + 1))
##########
import pandas as pd
import numpy as np
import pickle
from joblib import Parallel, delayed
import os
from skimage.util import view_as_windows



__all__ = ['factor_aggregation', 'get_max_drawdown', 'multi_processing_joblib', 'replace_inf', 'replace_zero', 'pd_writer', 'read_pickle', 'rolling_window', 'rolling_window_upgrade',\
           'save_pickle']

def factor_aggregation(factor_path):
    """
    read factors form the specified folder and aggregate the factors into a dataframe
    :param factor_path: str
        factor storage path
    :return: dataframe
        aggregated factor matrix, each column is a factor
    """
    factors = sorted([i for i in os.listdir(factor_path) if i.endswith('h5')])
    factors_list = [os.path.join(factor_path, i) for i in factors]

    factor_agg_df = None
    for i, i_name in enumerate(factors_list):
        factor = pd.read_hdf(i_name)
        factor_agg_df = factor if factor_agg_df is None else pd.concat([factor_agg_df, factor], axis=1)

    return factor_agg_df


def get_max_drawdown(ret_list, type='cumsum'):
    """
    calculate max drawdown, start date and end date of the max drawdown
    :param ret_list: array_like, one dimension
        yield curve or cumulative yield curve
    :param type: str
        可选cumsum或share，对应的输入分别是累计收益和分笔收益
    :return: float, datetime, datetime
        max_drawdown, max_drawdown_start_time, max_drawdown_end_time
    """
    assert isinstance(ret_list, pd.Series) or isinstance(ret_list, np.ndarray) or isinstance(ret_list, list)
    if isinstance(ret_list, np.ndarray):
        assert ret_list.shape[1] == 1
    if any([isinstance(ret_list, np.ndarray), isinstance(ret_list, list)]):
        ret_list = pd.Series(ret_list)
    if type == 'time_share':
        ret_list = ret_list.cumsum()
    ret_list1 = ret_list.expanding().max()
    ret_list2 = ret_list - ret_list1
    max_drawdown = ret_list2.min()
    if max_drawdown == 0:
        print('no drawdown')
        return
    else:
        max_drawdown_end_time = ret_list2.idxmin()
        max_drawdown_start_time = ret_list[:ret_list2.idxmin()].idxmax()
        return max_drawdown, max_drawdown_start_time, max_drawdown_end_time


def multi_processing_joblib(data, func, n_jobs=12, **kwargs):
    """
    cross-section multi-process for the dataframe
    :param data: array_like
        the raw data
    :param func:
        the function acting on dataframe
    :param n_jobs: int
        the number of cores used, if n_jobs=-1, all cores will be used
    :param kwargs:
        the parameters in the param func.
    :return: dataframe
        the data after the use of function
    """
    if not (isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.DataFrame, np.ndarray')
    if isinstance(data, pd.DataFrame):
        results = Parallel(n_jobs=n_jobs, max_nbytes='1G')(delayed(func)(data[i], **kwargs) for i in data.columns)
        results_df = pd.DataFrame(results, index=data.columns, columns=data.index)
    else:
        results = Parallel(n_jobs=n_jobs, max_nbytes='1G')(delayed(func)(data[:,i], **kwargs) for i in range(data.shape[1]))
        results_df = np.array(results)
    return results_df.T


def replace_inf(data, x=np.nan):
    '''replace inf to a predefined number for the input data
    parameters
    --------------------------------------------------
    data: dataframe, series or ndarray
        the data which contains inf
    x: int, float or np.nan, optional (default=np.nan)
        the value used to replace inf
    --------------------------------------------------  
    return
    --------------------------------------------------
    data: input data whose inf has been replaced
        the data whose inf is replaced
    --------------------------------------------------
    '''
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), 'the data structure of input is illegal'
    if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        data = data.replace([-np.inf, np.inf], x)
    elif isinstance(data, np.ndarray):
        data[np.isinf(data)] = x
    return data


def replace_zero(data, x=np.nan):
    """
    replace 0 to a predefined number for the input data
    :param data: dataframe, series or np.ndarray
        the data which contains 0
    :param x: int, float or np.nan, optional (default=np.nan)
        the value used to replace 0
    :return: same data structure as input data
        input data whose 0 has been replaced
    """
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), \
        'the data structure of input is illegal, must be pd.Series, pd.DataFrame or np.ndarray'
    if isinstance(data, np.ndarray):
        data = data + 0.  # 下述转化对int类型的ndarray无效，因此事先将数据类型转为float
    data[abs(data) < 1e-8] = x
    return data


def pd_writer(sig, savepath):
    """
    把df写成h5文件并保存
    : param sig: dataframe
        待写入和保存的df
    : param savepath: str
        保存路径
    : return: None
    """
    sig_name = sig.columns[0]
    file_name = os.path.join(savepath, sig_name + '.h5')
    if os.path.exists(file_name):
        #sigold = IO.read_data(alt = file_name)
        sigold = pd.read_hdf(file_name)
        sigold = sigold[~sigold.index.isin(sig.index)]
        signew = pd.concat([sigold, sig], axis=0).sort_index()
    else:
        signew = sig
    signew.to_hdf(file_name, key=sig_name)


def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict


def rolling_window(data, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    # 这是后面算子计算的辅助函数
    if data.ndim != 1:
        raise ValueError('input data must be a 1D array.')
    shape = data.shape[:-1] + (data.shape[-1] - window + 1, window)
    strides = data.strides + (data.strides[-1],)
    rolling_table = np.array(np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides))
    return rolling_table


def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    elif data.ndim == 2:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding


def save_pickle(save_dict, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict, input, protocol=pickle.HIGHEST_PROTOCOL)
    return



##########

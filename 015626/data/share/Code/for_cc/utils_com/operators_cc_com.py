# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 18:06:04 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from joblib import Parallel, delayed
import h5py
from rolling_adj import *

def check_h5_keys(file_path):
    holder = []
    with h5py.File(file_path, 'r') as f:
        for key in f.keys():
            holder.append(key)
    return holder

def no_rank(data, d = 1200, min_periods = 10):
    # moving time-series rank for the past d periods
    data1 = data.copy()
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), 'input must be a series, dataframe or ndarray'

    return data1.copy()

def rank_data(data):
    n = len(data)
    if n < 1:
        return np.nan
    elif n == 1:
        return 0.0
    data = np.array(data)
    current_value = data[-1]
    less = np.sum(data < current_value)
    equal = np.sum(data == current_value)
    rank = less + (equal + 1) / 2
    return 2 * ((rank - 1) / (n - 1)) - 1
    
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

def rolling_norm_raw(data, window):
    if len(data) == 0:
        return np.nan 
    elif len(data) == 1:
        return 0
    else:
        lm = nanmin_np(data[-window:])
        return 2 * (data[-1] - lm) / r(nanmax_np(data[-window:]) - lm) - 1

def calc_zscore_raw(dat1, window):
    if len(dat1) == 0:
        return np.nan 
    elif len(dat1) == 1:
        return 0
    else:
        dat = dat1[-window:]
        result = (dat[-1] - nanmean_np(dat)) / r(nanstd_np(dat, ddof = 1))
        if result > 5:
            return 5
        elif result < -5:
            return -5
        else:
            return result

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

def ts_std(df1, d, mc = 1):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_std(df1, window=d, min_count=mc, axis=0, ddof=1),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_std(df1, window=d, min_count=mc, axis=0, ddof=1),
                           index=df1.index, name=df1.name)
    return output

def ts_mean(df1, d, mc = 1):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_mean(df1, window=d, min_count=mc, axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_mean(df1, window=d, min_count=mc, axis=0),
                           index=df1.index, name=df1.name)
    return output

def ts_max(df1, d, mc = 1):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_max(df1, window=d, min_count=mc, axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_max(df1, window=d, min_count=mc, axis=0),
                           index=df1.index, name=df1.name)
    return output

def ts_min(df1, d, mc = 1):
    # moving time-series rank for the past d periods
    if isinstance(df1, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(df1, window=d, min_count=mc, axis=0),
                              index=df1.index, columns=df1.columns)
    elif isinstance(df1, pd.Series):
        output = pd.Series(bk.move_min(df1, window=d, min_count=mc, axis=0),
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
    c = nanmean_np(b[:,-5:], axis=1)
    flag = np.sum(np.isnan(a), axis=1) 
    flag = np.where(flag <= d - int(d / 2), 1, np.nan)
    output.iloc[d - 1:] = c * flag
    return output


def multi_processing_joblib(df, func, n_jobs, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T

def r(data, x=np.nan):
    try:
        data[abs(data) < 1e-8] = x
        return data
    except:
        if (abs(data) < 1e-8):
            return np.nan
        else:
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


    
def cross_ih(df):
    df[~np.isfinite(abs(df))] = np.nan
    if (isinstance(df, np.ndarray)):
        
        if len(np.shape(df)) != 1:
            a = df   
            b = (np.nansum((a == 0), axis = 1)>30)
            a[b == True] = np.nan
            a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
        else:
            a = df
            b = (np.nansum((a == 0))>30)
            if b == True:
                a = np.nan
            else:
                a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))
    else:
        a = df.copy().values
        if (isinstance(df, pd.DataFrame)):
            b = (np.nansum((a == 0), axis = 1)>30)
            a[b == True] = np.nan
            a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])

        else:
            b = (np.nansum((a == 0))>30)
            if b == True:
                a = np.nan
            else:
                a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))

  
    return a



def cross4_ih(df):
    if (isinstance(df, np.ndarray)):
        if len(np.shape(df)) != 1:
            a = df   
            b = (np.nansum((a == 0), axis = 1)>20)
            a[b == True] = np.nan
            a[a==0] = np.nan 
            #a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
        else:
            a = df
            b = (np.nansum((a == 0))>20)
            if b == True:
                a[:] = np.nan
            #else:
                #a = np.clip(a, np.nanpercentile(a, 1), np.nanpercentile(a, 99))
    else:
        a = df.copy().values
        if (isinstance(df, pd.DataFrame)):
            b = (np.nansum((a == 0), axis = 1)>20)
            a[b == True] = np.nan
            #a = np.array([np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99)) for x in a])
            a[a==0] = np.nan 
        else:
            b = (np.nansum((a == 0))>20)
            if b == True:
                a[:] = np.nan
            #else:
                #a = np.clip(x, np.nanpercentile(x, 1), np.nanpercentile(x, 99))

        
    return a
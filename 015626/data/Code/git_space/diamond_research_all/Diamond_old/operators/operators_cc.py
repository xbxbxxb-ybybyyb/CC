# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 18:06:04 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from joblib import Parallel, delayed

def rolling_norm(sig, window=1200, method='max_min'):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
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
            return 2 * signal - 1    
        elif method == 'ts_rank':
            if isinstance(sig, pd.DataFrame):
                signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                      index=sig.index, columns=sig.columns)
            elif isinstance(sig, pd.Series):
                signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, name=sig.name)
            return signal


def ts_rank(df1, d= 1200):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output


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
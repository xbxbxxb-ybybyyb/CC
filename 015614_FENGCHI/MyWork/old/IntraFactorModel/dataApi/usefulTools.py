# All rights reserved; those responsible for unauthorized reproduction will be prosecuted.
__author__ = 'hanxu'
__nickname__ = 'snowflake'
__email__ = 'hanxu@htsc.com'

import bottleneck
import numpy as np
import pandas as pd


def frame2arr(df, minutes=242):

    return df.values.reshape(df.shape[0] // minutes, minutes, df.shape[1]).transpose(1, 0, 2)

def arr2frame(arr, index, columns):

    return pd.DataFrame(arr.transpose(1, 0, 2).reshape(arr.shape[0] * arr.shape[1], arr.shape[2]),
                        index=index, columns=columns)

def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)

def delay(arr, l=1):

    return fill_nan(arr[:-l], l)

def delta(arr, l=1):

    return arr - delay(arr, l)

def ts_mean(arr, l):

    return bottleneck.move_mean(arr, l, axis=0)

def ts_median(arr, l):

    return bottleneck.move_median(arr, l, axis=0)

def ts_min(arr, l):

    return bottleneck.move_min(arr, l, axis=0)

def ts_max(arr, l):

    return bottleneck.move_max(arr, l, axis=0)

def ts_argmax(arr, l):

    return bottleneck.move_argmax(arr, l, axis=0)

def ts_argmin(arr, l):

    return bottleneck.move_argmin(arr, l, axis=0)

def ts_rank(arr, l):

    return bottleneck.move_rank(arr, l, axis=0)

def ts_std(arr, l):

    return bottleneck.move_std(arr, l, axis=0)

def ts_var(arr, l):

    return bottleneck.move_var(arr, l, axis=0)

def ts_sum(arr, l):

    return bottleneck.move_sum(arr, l, axis=0)

def cross_rank(arr):

    return bottleneck.nanrankdata(arr, axis=2)

def cross_pct(arr):

    rank = bottleneck.nanrankdata(arr, axis=2)
    max_rank = np.nanmax(rank, axis=2)
    return (rank.transpose(2, 0, 1) / max_rank).transpose(1, 2, 0)

def ts_corr(y, x, l):

    cx = ts_sum(x, l)
    cy = ts_sum(y, l)
    cx2 = ts_sum(x ** 2, l)
    cy2 = ts_sum(y ** 2, l)
    cxy = ts_sum(x * y, l)
    return (l * cxy - cx * cy) / np.sqrt((l * cx2 - cx ** 2) * (l * cy2 - cy ** 2))

def ts_beta(y, x, l):

    cx = ts_sum(x, l)
    cy = ts_sum(y, l)
    cx2 = ts_sum(x ** 2, l)
    cxy = ts_sum(x * y, l)
    return (l * cxy - cx * cy) / (l * cx2 - cx ** 2)

def ts_cumsum(arr):

    return np.nancumsum(arr, axis=0)

def ts_cumprod(arr):

    return np.nancumprod(arr, axis=0)

def ts_cummax(arr):

    return np.maximum.accumulate(arr, axis=0)

def ts_cummin(arr):

    return np.minimum.accumulate(arr, axis=0)

def ts_ewm(arr, l, ewa=0.9):

    weight = ewa ** np.arange(l)
    weight /= weight.sum()
    return fill_nan(np.apply_along_axis(np.convolve, 0, arr, weight, 'valid'), l - 1)

def ts_argcummax(arr):

    arg = np.arange(arr.shape[0]).repeat(arr.shape[1] * arr.shape[2]).reshape(arr.shape[0], arr.shape[1], arr.shape[2])
    arg[np.maximum.accumulate(arr, axis=0) != arr] = 0
    return np.maximum.accumulate(arg, axis=0)

def ts_argcummin(arr):

    arg = np.arange(arr.shape[0]).repeat(arr.shape[1] * arr.shape[2]).reshape(arr.shape[0], arr.shape[1], arr.shape[2])
    arg[np.minimum.accumulate(arr, axis=0) != arr] = 0
    return np.maximum.accumulate(arg, axis=0)

def ts_cumstd(arr, min_count=10):

    cx = ts_cumsum(arr).transpose(1, 2, 0)
    cx2 = ts_cumsum(arr ** 2).transpose(1, 2, 0)
    std = np.sqrt((cx2 - cx ** 2 / (np.arange(arr.shape[0]) + 1)) / np.arange(arr.shape[0])).transpose(2, 0, 1)
    std[:min_count] = np.nan
    return std

def ts_cummean(arr):

    return (ts_cumsum(arr).transpose(1, 2, 0) / (np.arange(arr.shape[0]) + 1)).transpose(2, 0, 1)

def ts_cumcorr(y, x, min_count=10):

    cx = ts_cumsum(x).transpose(1, 2, 0)
    cy = ts_cumsum(y).transpose(1, 2, 0)
    cx2 = ts_cumsum(x ** 2).transpose(1, 2, 0)
    cy2 = ts_cumsum(y ** 2).transpose(1, 2, 0)
    cxy = ts_cumsum(x * y).transpose(1, 2, 0)
    corr = (((np.arange(x.shape[0]) + 1) * cxy - cx * cy) / np.sqrt(
        ((np.arange(x.shape[0]) + 1) * cx2 - cx ** 2) * ((np.arange(y.shape[0]) + 1) * cy2 - cy ** 2))).transpose(2, 0,
                                                                                                                  1)
    corr[:min_count] = np.nan
    return corr

def ts_cumbeta(y, x, min_count=10):

    cx = ts_cumsum(x).transpose(1, 2, 0)
    cy = ts_cumsum(y).transpose(1, 2, 0)
    cx2 = ts_cumsum(x ** 2).transpose(1, 2, 0)
    cxy = ts_cumsum(x * y).transpose(1, 2, 0)
    beta = ((np.arange(x.shape[0]) + 1) * cxy - cx * cy) / ((np.arange(x.shape[0]) + 1) * cx2 - cx ** 2).transpose(2, 0,
                                                                                                                   1)
    beta[:min_count] = np.nan
    return beta

def ts_decaylinear(arr, l):

    weight = np.arange(l).astype(float) + 1
    weight /= weight.sum()
    return fill_nan(np.apply_along_axis(np.convolve, 0, arr, weight, 'valid'), l - 1)

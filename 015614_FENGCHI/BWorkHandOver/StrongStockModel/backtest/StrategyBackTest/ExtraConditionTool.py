# @Time : 2022/4/25 10:23
# @Author : Zhichen Lu
# @File : ExtraConditionTool.py
import pandas as pd
import numpy as np
import bottleneck

def fill_nan(arr, l):
    return np.pad(arr, ((l, 0), (0, 0), (0, 0)), mode='constant', constant_values=np.nan)


def delay(arr, l=1):
    return fill_nan(arr[:-l], l)


def calc_recent_count(signal, window=20,bars=7):
    signal_arr = signal.values.reshape(signal.shape[0] // bars, bars, signal.shape[-1])
    idx_arr = np.empty(signal_arr.shape)
    for idx in range(bars):
        idx_arr[:, idx, :] = np.ones((idx_arr.shape[0], idx_arr.shape[-1])) * idx + 1
    idx_arr[~signal_arr] = np.nan
    first_signal = np.nanmin(idx_arr, axis=1)[:, None, :]
    is_triggered_first = np.isclose(first_signal, idx_arr)
    recent_20d_s_count = bottleneck.move_sum(np.where(is_triggered_first, 1, 0), axis=0, window=window)
    recent_20d_s_count = delay(recent_20d_s_count, 2)
    recent_20d_s_count = pd.DataFrame(recent_20d_s_count.reshape(signal.shape), index=signal.index, columns=signal.columns)
    barly_recent_20d_s_count = recent_20d_s_count.sum(axis=1).unstack()
    barly_recent_20d_ratio = (barly_recent_20d_s_count.T / barly_recent_20d_s_count.sum(axis=1)).T
    return barly_recent_20d_ratio, barly_recent_20d_s_count


def get_barly_trigger(long_signal, short_signal):
    signal = []
    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    for idx, time_point in enumerate(bar_list):
        future_window = 8 - idx
        temp_long = long_signal[future_window].swaplevel(0, 1).loc[[time_point]].swaplevel(0, 1).notnull()
        for short_window in range(1, future_window):
            temp_short = short_signal[short_window].swaplevel(0, 1).loc[[time_point]].swaplevel(0, 1).notnull()
            temp_long = temp_long & (~temp_short)
        signal.append(temp_long)
    signal = pd.concat(signal).sort_index()
    return signal
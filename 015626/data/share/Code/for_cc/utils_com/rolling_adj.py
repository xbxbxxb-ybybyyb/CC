
import numpy as np
# from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from utils_zsj import *
from skimage.util import view_as_windows
from numba import njit

@njit
def irr_filter_numba(input_signal, window):
    alpha = 2 / (window + 1)
    b0 = alpha - (alpha ** 2) / 4
    b1 = (alpha ** 2) / 2
    b2 = -(alpha - (3 * alpha ** 2) / 4)
    a1 = -2 * (1 - alpha)
    a2 = (1 - alpha) ** 2

    N = len(input_signal)
    y = np.zeros(N)
    for n in range(N):
        if n == 0:
            y[n] = b0 * input_signal[n]
        elif n == 1:
            y[n] = b0 * input_signal[n] + b1 * input_signal[n-1] - a1 * y[n-1]
        else:
            y[n] = (b0 * input_signal[n] + b1 * input_signal[n-1] + b2 * input_signal[n-2] - a1 * y[n-1] - a2 * y[n-2])
    return y

def r(data, x=np.nan):
    try:
        data[abs(data) < 1e-8] = x
        return data
    except:
        if (abs(data) < 1e-8):
            return np.nan
        else:
            return data

def irr_filter4(data, coef, bbb):
    window = bbb
    sig1_list = nanforward_fill(data[-window * 6 :])
    return irr_filter_numba(sig1_list[-int(window * coef):], int(window * coef))[-1]

def rolling_window_upgrade(data, window):
    # 升级版rolling_window，可以处理二维数组的情况
    if data.ndim not in [1, 2]:
        raise ValueError('input data must be a 1D or 2D array.')
    if data.ndim == 1:
        data_expanding = view_as_windows(data, (window,))
    elif data.ndim == 2:
        data_expanding = view_as_windows(data, (window, 1))[..., 0]
    return data_expanding

def irr_filter(input_signal, window):
    alpha = 2 / (window + 1)
    b0 = alpha - (alpha ** 2) / 4
    b1 = (alpha ** 2) / 2
    b2 = -(alpha - (3 * alpha ** 2) / 4)
    a1 = -2 * (1 - alpha)
    a2 = (1 - alpha) ** 2
    y = np.zeros_like(input_signal)
    for n in range(len(input_signal)):
        if n == 0:
            y[n] = b0 * input_signal[n]
        elif n == 1:
            y[n] = b0 * input_signal[n] + b1 * input_signal[n-1] - a1 * y[n-1]
        else:
            y[n] = (b0 * input_signal[n] + b1 * input_signal[n-1] + b2 * input_signal[n-2] - a1 * y[n-1] - a2 * y[n-2])
    return y



def ewma(input_signal, window):
    alpha = 1 / (window + 1)
    y = np.zeros_like(input_signal)
    for n in range(len(input_signal)):
        if n == 0:
            y[n] = input_signal[n]
        else:
            y[n] = input_signal[n] * alpha + y[n-1] * (1-alpha)
    return y
    
##########################################################################################################################################
import numpy as np
import pandas as pd
from skimage.util import view_as_windows

def nanforward_fill(arr1):
    """
    使用前向填充（Forward Fill）填充数组中的 NaN 值。
    """
    if (type(arr1) == float) or (type(arr1) == int):
        return arr1
    if type(arr1) != np.ndarray:
        arr = np.array(arr1)
    else:
        arr = arr1
    arr = arr.astype(float).copy() # 确保数组为浮点类型
    mask = np.isnan(arr)
    if not mask.any():
        return arr
    non_nan_idx = np.where(~mask)[0]
    non_nan_vals = arr[non_nan_idx]

    nan_idx = np.where(mask)[0]

    indices = np.searchsorted(non_nan_idx, nan_idx, side='right') - 1
    valid = indices >= 0 # 过滤无效索引（如开头的 NaN）
    arr[nan_idx[valid]] = non_nan_vals[indices[valid]]
    if type(arr1) == np.ndarray:
        return arr
    else:
        return arr.tolist()

def ema_1(factor_array2,d,alpha):
    if 1 / alpha > len(factor_array2):
        return np.nan
    if d > len(factor_array2):
        d = len(factor_array2)
    factor_array1 = factor_array2[-d:]
    if type(factor_array1) != np.ndarray:
        factor_array = np.array(factor_array1)
        weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
        flag = np.isnan(factor_array) | np.isnan(weight)
        flag1 = np.sum(flag, axis=-1)  # 缺失值个数
        flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
        if flag1 > 0:
            factor_array[flag] = np.nan
            weight[flag] = np.nan
        factor = np.nansum(factor_array[-d:] * weight) / np.nansum(weight) # truncate_ema_1

    elif type(factor_array1) == np.ndarray:
        weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
        flag = np.isnan(factor_array1) | np.isnan(weight)
        flag1 = np.sum(flag, axis=-1)  # 缺失值个数
        flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
        if flag1 > 0:
            factor_array1[flag] = np.nan
            weight[flag] = np.nan
        factor = np.nansum(factor_array1[-d:] * weight) / np.nansum(weight) # truncate_ema_1

    return factor

def ema_span_1(factor_array, d, span):
    return ema_1(factor_array, d = d, alpha=2 / (span + 1))

def cci(typical_price, time_period=14):
    typical_price_ma = bk.move_mean(typical_price,window = time_period, min_count = int(time_period/2))
    tmp = abs(typical_price - typical_price_ma)
    typical_price_mean_deviation = bk.move_mean(tmp,window = time_period,min_count = int(time_period/2))
    price_cci = (typical_price - typical_price_ma) / (typical_price_mean_deviation)
    return price_cci
def irr_filter_raw(input_signal, window):
    is1 = np.array(input_signal)
    is2 = nanforward_fill(is1)
    return(irr_filter_numba(is2, window))

def chip_dis_raw(price_array1, volume_array1, window):
    if len(price_array1) < 2:
        return np.nan
    else:
        price_array = price_array1[-window:]
        volume_array = volume_array1[-window:]

        _r = np.nansum((price_array < price_array[-1]) * volume_array) / np.nansum(volume_array)
        return _r

def new_corr(a1, b1):

    if (len(a1) == 0) or (len(b1) == 0) or np.isnan(len(a1)) or np.isnan(len(b1)):
        return np.nan
    if len(a1) != len(b1):
        lth = np.nanmin([len(a1), len(b1)])
        a1 = a1[-lth:]
        b1 = b1[-lth:]
    a = np.array(a1)
    b = np.array(b1)
    fuck = np.column_stack((a, b))
    fuck = fuck[~np.isnan(fuck).any(axis = 1)]
    result = np.corrcoef(fuck[:, 0], fuck[:, 1])[0][1]
    return result

def irr_filter2(data, coef, bbb):
    window = bbb
    sig1_list = nanforward_fill(data[-window * 6 :])
    return irr_filter(sig1_list[-int(window * coef):], int(window * coef))[-1]

def chip_dis_array(price_array, volume_array):
    if len(price_array) < 2:
        return np.nan
    else:
        window = len(price_array)
        _r = np.nansum((price_array < price_array[-1]) * volume_array) / np.nansum(volume_array)
        return _r

def cross_hub_num_array(data_array, d):
    if len(data_array) < 2:
        return np.nan 
    if d > len(data_array):
        d = len(data_array)
    # 过去一段时间曲线穿越中枢的次数
    data_centralized = data_array - bk.move_mean(data_array,window = d,min_count = int(d/2))
    flag = (data_centralized[1:] * data_centralized[:-1]) < 0
    output = np.nansum(flag[-d:])
    return output


# ema加强版，严格好于ema
def irr_ma(factor, window):
    assert type(factor) == pd.Series
    jd = window * 5
    rw = rolling_window_upgrade(factor.ffill().values, jd)
    factor = pd.Series([np.nan] * (jd - 1) + [irr_filter(item, window)[-1] for item in rw], index = factor.index)
    return factor


def nanargmax_new(arr):
    max_val = nanmax_np(arr)
    if np.isnan(max_val):
        last_index = -1
    else:
        indices = np.where(arr == max_val)[0]
        last_index = int(max(indices)-len(arr)) if indices.size > 0 else -1
    return last_index 
    
def nanargmin_new(arr):
    min_val = nanmin_np(arr)
    if np.isnan(min_val):
        last_index = -1
    else:
        indices = np.where(arr == min_val)[0]
        last_index = int(max(indices) -len(arr)) if indices.size > 0 else -1
    return last_index

def move_mean_bk(data, window, min_count=1, axis = 0):
    if len(data) == 0:
        return data
    elif len(data) == 1:
        return data
    elif len(data) < window:
        wd = len(data)
        return bk.move_mean(data, wd, min_count = int(wd/2), axis = axis)
    else:
        return bk.move_mean(data, window, min_count = min_count, axis = axis)


def move_median_bk(data, window, min_count=1, axis = 0):
    if len(data) == 0:
        return data
    elif len(data) == 1:
        return data
    elif len(data) < window:
        wd = len(data)
        return bk.move_median(data, wd, min_count = int(wd/2), axis = axis)
    else:
        return bk.move_median(data, window, min_count = min_count, axis = axis)


def move_sum_bk(data, window, min_count=1, axis = 0):
    if len(data) == 0:
        return data
    elif len(data) == 1:
        return data
    elif len(data) < window:
        wd = len(data)
        return bk.move_sum(data, wd, min_count = int(wd/2), axis = axis)
    else:
        return bk.move_sum(data, window, min_count = min_count, axis = axis)

def move_min_bk(data, window, min_count=1, axis = 0):
    if len(data) == 0:
        return data
    elif len(data) == 1:
        return data
    elif len(data) < window:
        wd = len(data)
        return bk.move_min(data, wd, min_count = int(wd/2), axis = axis)
    else:
        return bk.move_min(data, window, min_count = min_count, axis = axis)

def move_max_bk(data, window, min_count=1, axis = 0):
    if len(data) == 0:
        return data
    elif len(data) == 1:
        return data
    elif len(data) < window:
        wd = len(data)
        return bk.move_max(data, wd, min_count = int(wd/2), axis = axis)
    else:
        return bk.move_max(data, window, min_count = min_count, axis = axis)

def move_rank_bk(data, window, min_count=1, axis = 0):
    if len(data) == 0:
        return data
    elif len(data) == 1:
        return 0
    elif len(data) < window:
        wd = len(data)
        return bk.move_rank(data, wd, min_count = int(wd/2), axis = axis)
    else:
        return bk.move_rank(data, window, min_count = min_count, axis = axis)


def move_std_bk(data, window, min_count=1, ddof = 0, axis = 0):

    if len(data) <= 1:
        return data
    elif len(data) < window:
        wd = len(data)
        return bk.move_std(data, wd, min_count = int(wd/2), ddof = ddof, axis = axis)
    else:
        try:
            return bk.move_std(data, window, min_count = min_count, ddof = ddof, axis = axis)
        except:
            if type(data) == np.ndarray:
                return np.array([np.nan] * len(data))
            else:
                return [np.nan] * len(data)

def nanmean_np(data, axis = 0):
    if len(data) == 0:
        return np.nan
    else:
        return np.nanmean(data, axis = axis)


def nanmin_np(data, axis = 0):
    if len(data) == 0:
        return np.nan
    else:
        return np.nanmin(data, axis = axis)


def nanmax_np(data, axis = 0):
    if len(data) == 0:
        return np.nan
    else:
        return np.nanmax(data, axis = axis)

def nansum_np(data, axis = 0):
    if len(data) == 0:
        return np.nan
    else:
        return np.nansum(data, axis = axis)


def nanmedian_np(data, axis = 0):
    if len(data) == 0:
        return np.nan
    else:
        return np.nanmedian(data, axis = axis)



def nanstd_np(data, ddof = 0, axis = 0):

    if len(data) == 0:
        return np.nan
    else:
        try:
            return np.nanstd(data, ddof = ddof, axis = axis)
        except:
            if type(data) == np.ndarray:
                return np.array([np.nan] * len(data))
            else:
                return [np.nan] * len(data)
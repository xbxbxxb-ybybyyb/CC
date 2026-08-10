from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np

from skimage.util import view_as_windows

def nanforward_fill(arr):
    """
    使用前向填充（Forward Fill）填充数组中的 NaN 值。
    """
    arr = arr.astype(float).copy()  # 确保数组为浮点类型
    mask = np.isnan(arr)
    if not mask.any():
        return arr
    non_nan_idx = np.where(~mask)[0]
    non_nan_vals = arr[non_nan_idx]

    nan_idx = np.where(mask)[0]

    indices = np.searchsorted(non_nan_idx, nan_idx, side='right') - 1
    valid = indices >= 0  # 过滤无效索引（如开头的 NaN）
    arr[nan_idx[valid]] = non_nan_vals[indices[valid]]
    return arr

def ema_archive(factor_array,d,alpha):
    factor_array = np.array(factor_array)
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    flag = np.isnan(factor_array) | np.isnan(weight)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    factor_array[flag] = np.nan
    weight[flag] = np.nan
    factor = nansum_np(factor_array[-d:] * weight) / nansum_np(weight) # truncate_ema_1
    return factor


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


class fast_fac_9_df(FutureFactor): 

    def __init__(self, ticker, freq = 1):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        self.days_past = int(freq) * 1 # different product should be different
        self.required_columns = ['close_secmain','high_secmain','low_secmain']
        self.instrument_type = 'second_main' #second_main
        #normalize_size = 2*coef
        self.normalize_size = 300
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.pre_factor_list = []        
    
    def calculate(self, data):
        a = 180
        b = 60
        c = 5
        d = 1
        close = data['close_secmain']
        high = data['high_secmain']
        low = data['low_secmain']
        low_n = move_min_bk(low,window = a, min_count = int(a/2))
        high_n = move_max_bk(high,window = a,min_count = int(a/2))
        temp1 = high_n - low_n
        temp1[abs(temp1)<1e-8] = np.nan        
        temp2 = (close- low_n) / temp1
        b_low = move_min_bk(temp2,window = b,min_count = int(b/2))
        b_high = move_max_bk(temp2,window = b, min_count = int(b/2))
        temp3 = b_high - b_low        
        temp3[abs(temp3)<1e-8] = np.nan
        temp4 = (temp2 - b_low) / temp3
        pre_factor = temp4[-1] / 3 + irr_filter(temp4[-25:], 5)[-1]
        self.pre_factor_list.append(pre_factor)
        factor = pre_factor - ema_1(self.pre_factor_list[-30:], 30, 1/11)
        return factor

    def pre_calculate(self,data):  
        self.pre_factor_list = []        
        for i in range(29, -1, -1):
            if i == 0:
                close = data['close_secmain'][-266:]
                high = data['high_secmain'][-266:]
                low = data['low_secmain'][-266:]
                if len(close) < 90:
                    self.pre_factor_list.append(np.nan)  
                    continue
                low_n = move_min_bk(low,window = 180, min_count = 90)
                high_n = move_max_bk(high,window = 180,min_count = 90)
                temp1 = high_n - low_n
                temp1[abs(temp1)<1e-8] = np.nan        
                temp2 = (close- low_n) / temp1
                b_low = move_min_bk(temp2,window = 60,min_count = 30)
                b_high = move_max_bk(temp2,window = 60, min_count = 30)
                temp3 = b_high - b_low        
                temp3[abs(temp3)<1e-8] = np.nan
                temp4 = (temp2 - b_low) / temp3
                pre_factor = temp4[-1] / 3 + irr_filter(temp4[-25:], 5)[-1]
                self.pre_factor_list.append(pre_factor)
            else:
                close = data['close_secmain'][-(266+i):-i]
                high = data['high_secmain'][-(266+i):-i]
                low = data['low_secmain'][-(266+i):-i]
                if len(close) < 90:
                    self.pre_factor_list.append(np.nan)  
                    continue
                low_n = move_min_bk(low,window = 180, min_count = 90)
                high_n = move_max_bk(high,window = 180,min_count = 90)
                temp1 = high_n - low_n
                temp1[abs(temp1)<1e-8] = np.nan        
                temp2 = (close- low_n) / temp1
                b_low = move_min_bk(temp2,window = 60,min_count = 30)
                b_high = move_max_bk(temp2,window = 60, min_count = 30)
                temp3 = b_high - b_low        
                temp3[abs(temp3)<1e-8] = np.nan
                temp4 = (temp2 - b_low) / temp3
                pre_factor = temp4[-1] / 3 + irr_filter(temp4[-25:], 5)[-1]
                self.pre_factor_list.append(pre_factor)            

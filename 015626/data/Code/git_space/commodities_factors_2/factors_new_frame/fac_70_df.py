from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





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



def rolling_normalize_array(sig, window):

    sig_max = move_max_bk(sig,window,min_count = int(window/2))

    sig_min = move_min_bk(sig,window,min_count = int(window/2))

    sig_roll_norm = (sig - sig_min) / (sig_max - sig_min) * 2 - 1

    return sig_roll_norm



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



class fac_70_df(FutureFactor):    



    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['oi', 'close']

        self.normalize_size = 1

        self.normalize_type = 'ts_rank'

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 12 # different product should be different

        self.fac1_list = []

        self.fac2_list = []

        self.fac3_list = []

        self.fac4_list = []

        self.factor_ema_list = []

        

    def calculate(self, data):                

        

        coef = self.bars_dict[self.ticker] / self.freq

        c1 = int(coef / 2)

        c2 = int(coef * 2)

        l = max(c2, 100)

        

        cls = data['close'][-l:]

        oi = data['oi'][-l:]

        

        fac1_ = abs(corrcoef_np(cls[-5:],oi[-5:])[1,0])

        fac2_ = abs(corrcoef_np(cls[-25:],oi[-25:])[1,0])

        self.fac1_list.append(fac1_)

        self.fac2_list.append(fac2_)



        cls_diff = cls[1:] - cls[:-1]

        cls_diff_mean = nanmean_np(cls_diff[-5:])

        cls_diff_std = nanstd_np(cls_diff[-5:],ddof = 1)

        if abs(cls_diff_std) < 1e-8:

            cls_diff_std = np.nan

        self.fac3_list.append(cls_diff_mean / cls_diff_std)



        cls_diff_mean_ = nanmean_np(cls_diff[-25:])

        cls_diff_std_ = nanstd_np(cls_diff[-25:],ddof = 1)

        if abs(cls_diff_std_) < 1e-8:

            cls_diff_std_ = np.nan

        self.fac4_list.append(cls_diff_mean_ / cls_diff_std_)



        fac1 = np.array(self.fac1_list[-10:])

        fac2 = np.array(self.fac2_list[-10:])

        fac3 = np.array(self.fac3_list[-10:])

        fac4 = np.array(self.fac4_list[-10:])

        

        fac = fac3 * fac1 + fac2 * fac4

        fac[np.isnan(fac)] = 0

        co = cross_hub_num_array(cls[-25:], 10) + 1

        if abs(co) < 1e-8:

            co = np.nan

        factor_ema = ema_1(fac[-10:],10,1/3) / co

        self.factor_ema_list.append(factor_ema)

        if len(self.factor_ema_list) < 2400:

            print(len(self.factor_ema_list))

            raise ValueError('wrong length!')

        factor_rk = move_rank_bk(np.array(self.factor_ema_list),window = 1200, min_count = 600)



        

        cs = corrcoef_np(factor_rk[-c1:],cls[-c1:])[1,0]

        cl = corrcoef_np(factor_rk[-c2:],cls[-c2:])[1,0]



        if (cs < cl) | (cl < 0):

            factor = 0

        else:

            factor = factor_rk[-1]

        return factor

        

    def pre_calculate(self,data):

        self.fac1_list = []

        self.fac2_list = []

        self.fac3_list = []

        self.fac4_list = []

        self.factor_ema_list = []

        N = int(max(2000,1200+self.bars_dict[self.ticker]/self.freq * 2))

        for i in range(N):

            if i == 0:

                cls = data['close'][-25:]

                oi = data['oi'][-25:]

                fac1_ = abs(corrcoef_np(cls[-5:],oi[-5:])[1,0])

                fac2_ = abs(corrcoef_np(cls[-25:],oi[-25:])[1,0])

                self.fac1_list.append(fac1_)

                self.fac2_list.append(fac2_) 



                cls_diff = cls[1:] - cls[:-1]

                cls_diff_mean = nanmean_np(cls_diff[-5:])

                cls_diff_std = nanstd_np(cls_diff[-5:],ddof = 1)

                if abs(cls_diff_std) < 1e-8:

                    cls_diff_std = np.nan

                self.fac3_list.append(cls_diff_mean / cls_diff_std)



                cls_diff_mean_ = nanmean_np(cls_diff[-25:])

                cls_diff_std_ = nanstd_np(cls_diff[-25:],ddof = 1)

                if abs(cls_diff_std_) < 1e-8:

                    cls_diff_std_ = np.nan

                self.fac4_list.append(cls_diff_mean_ / cls_diff_std_)            

            else:

                cls = data['close'][-(25+i):-i]

                oi = data['oi'][-(25+i):-i]

                fac1_ = abs(corrcoef_np(cls[-5:],oi[-5:])[1,0])

                fac2_ = abs(corrcoef_np(cls[-25:],oi[-25:])[1,0])

                self.fac1_list.append(fac1_)

                self.fac2_list.append(fac2_)

                

                cls_diff = cls[1:] - cls[:-1]

                cls_diff_mean = nanmean_np(cls_diff[-5:])

                cls_diff_std = nanstd_np(cls_diff[-5:],ddof = 1)

                if abs(cls_diff_std) < 1e-8:

                    cls_diff_std = np.nan

                self.fac3_list.append(cls_diff_mean / cls_diff_std)



                cls_diff_mean_ = nanmean_np(cls_diff[-25:])

                cls_diff_std_ = nanstd_np(cls_diff[-25:],ddof = 1)

                if abs(cls_diff_std_) < 1e-8:

                    cls_diff_std_ = np.nan

                self.fac4_list.append(cls_diff_mean_ / cls_diff_std_)

        self.fac1_list.reverse()

        self.fac2_list.reverse()



        self.fac3_list.reverse()

        self.fac4_list.reverse()



        

        for i in range(N + 500):            

            if i == 0:       

                fac1 = np.array(self.fac1_list[-10:])

                fac2 = np.array(self.fac2_list[-10:])

                fac3 = np.array(self.fac3_list[-10:])

                fac4 = np.array(self.fac4_list[-10:])

                fac = fac3 * fac1 + fac2 * fac4

                co = cross_hub_num_array(data['close'][-25:], 10)

                if abs(co) < 1e-8:

                    co = np.nan

                factor_ema = ema_1(fac,10,1/3) / co

                self.factor_ema_list.append(factor_ema)

            else:

                fac1 = np.array(self.fac1_list[-(10+i):-i])

                fac2 = np.array(self.fac2_list[-(10+i):-i])

                fac3 = np.array(self.fac3_list[-(10+i):-i])

                fac4 = np.array(self.fac4_list[-(10+i):-i])

                #fac = nanforward_fill(fac3 * fac1 + fac2 * fac4)                

                co = cross_hub_num_array(data['close'][-(25+i):-i], 10)

                if abs(co) < 1e-8:

                    co = np.nan

                factor_ema = ema_1(fac,10,1/3) / co

                self.factor_ema_list.append(factor_ema)

        self.factor_ema_list.reverse()
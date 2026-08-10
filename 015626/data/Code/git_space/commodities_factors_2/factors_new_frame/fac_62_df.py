from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def nanforward_fill(arr):

    """

    使用前向填充（Forward Fill）填充数组中的 NaN 值。

    """

    arr = arr.astype(float).copy()  # 确保数组为浮点类型

    mask = np.isnan(arr)

    if not mask.any():

        return arr  # 如果没有 NaN，直接返回原数组



    # 获取非 NaN 值的索引和值

    non_nan_idx = np.where(~mask)[0]

    non_nan_vals = arr[non_nan_idx]



    # 获取 NaN 值的索引

    nan_idx = np.where(mask)[0]



    # 使用 searchsorted 找到每个 NaN 对应的最近非 NaN 索引

    indices = np.searchsorted(non_nan_idx, nan_idx, side='right') - 1

    valid = indices >= 0  # 过滤无效索引（如开头的 NaN）



    # 填充 NaN 值

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



class fac_62_df(FutureFactor):    

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = 1

        self.required_columns = ['close','high','low','tday']        

        normalize_size = 500

        normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__

        self.pre_factor_list = []



    def calculate(self, data):

        chigh = data['high']

        clow = data['low']

        cclose = data['close']

        ctday = data['tday']

        tdy = ctday[-1]

        ccls = cclose[-1]

        today_high = nanmax_np(chigh[ctday==tdy])

        today_low = nanmin_np(clow[ctday==tdy])

        self.pre_factor_list.append(-(today_high - ccls) / (today_high-today_low))

        factor_array = nanforward_fill(np.array(self.pre_factor_list[-6:]))        

        factor = ema_1(factor_array,6,1/3)

        tvol = nanstd_np(cclose[ctday == tdy])

        if abs(tvol) < 1e-8:

            tvol = np.nan            

        factor = factor / tvol

        return factor



    def pre_calculate(self, data):
        self.pre_factor_list = []

        for i in range(6, -1, -1):

            if i == 0:                

                chigh = data['high']

                clow = data['low']

                cclose = data['close']

                ctday = data['tday']




            else:                

                chigh = data['high'][:-i]

                clow = data['low'][:-i]

                cclose = data['close'][:-i]

                ctday = data['tday'][:-i]

            if len(ctday) < 1:
                self.pre_factor_list.append(np.nan)
                continue

            tdy = ctday[-1]

            ccls = cclose[-1]



            today_high = nanmax_np(chigh[ctday==tdy])

            today_low = nanmin_np(clow[ctday==tdy])

            self.pre_factor_list.append((-(today_high - ccls) / (today_high-today_low)))

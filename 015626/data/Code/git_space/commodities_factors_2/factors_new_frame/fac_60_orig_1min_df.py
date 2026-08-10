from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





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

    

class fac_60_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['close_secmain']

        self.normalize_size = 3000

        self.normalize_type = 'ts_rank'

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 1

        

    def calculate(self, data):

        cls = data['close_secmain'][-200:]

        cls_diff = cls[15:] - cls[:-15]

        cls_diff_sign = np.sign(cls_diff)

        cls_diff_std = move_sum_bk(cls_diff ** 2, window = 60, min_count = 30)

        factor_raw = cls_diff_sign * cls_diff_std

        factor = ema_1(factor_raw[-75:], 25 * 3, 1/(25+1))        

        return factor
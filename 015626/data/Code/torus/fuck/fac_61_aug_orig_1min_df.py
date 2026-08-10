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

    

class fac_61_aug_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['close_secmain','open_secmain']

        self.normalize_size = 6000

        self.normalize_type = 'ts_rank'

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 1

        self.prefactor_list = []

        

    def calculate(self, data):

        cls = data['close_secmain'][-200:]

        opn = data['open_secmain'][-200:]

        cdo_r = move_mean_bk(cls, window = 10, min_count = 1) - move_mean_bk(opn, window = 10, min_count = 1)

        factor = ema_1(cdo_r[-90:], 30 * 3, 1/(30 + 1))

        return factor
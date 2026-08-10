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

    

class fac_52_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.required_columns = ['close','twap']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = int(10 * self.bars_dict[ticker] / freq)

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 2

        

    def calculate(self, data):

        unit = self.freq

        aaa = nanmin_np([int(10 / unit), 5])

                

        twap = data['twap']

        close = data['close']

        fac1 = move_mean_bk(twap,window = aaa, min_count = 1)

        fac2 = move_mean_bk(close, window = aaa, min_count = 1)

        fac = -fac1 / fac2

        factor = ema_1(fac[-15:],15,1/6)

        return factor
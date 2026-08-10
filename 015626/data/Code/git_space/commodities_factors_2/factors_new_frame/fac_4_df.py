from rolling_adj import *

import numpy as np
from commodity_framework import FutureFactor


def ema_archive(factor_array, d, alpha):
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    flag = np.isnan(factor_array) | np.isnan(weight)
    factor_array[flag] = np.nan
    weight[flag] = np.nan
    factor = nansum_np(factor_array[-d:] * weight) / nansum_np(weight)
    return factor


def calculate_slope(y):
    x = np.cumsum(np.ones_like(y))
    slope = np.cov(x, y)[0, 1]
    return slope


class fac_4_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close']
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'

        self.ma_list = []
        self.ma_slope_list = []

    def calculate(self, data):
        c = data['close']

        aaa = 6
        bbb = 15
        ccc = 30
        ddd = 12

        ma = nanmean_np(c[-aaa:])
        self.ma_list.append(ma)
        ma_slope_15 = calculate_slope(np.array(self.ma_list[-bbb:]))
        ma_slope_60 = calculate_slope(np.array(self.ma_list[-ccc:]))
        ma_slope = ma_slope_15 + ma_slope_60
        self.ma_slope_list.append(ma_slope)
        sig = ema_1(np.array(self.ma_slope_list[-ddd:]), ddd, 1 / 4)
        return sig

    def pre_calculate(self, data):
        self.ma_list = []
        self.ma_slope_list = []
        c_all = data['close']

        aaa = 6
        bbb = 15
        ccc = 30

        n = 50
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
            else:
                c = c_all[:-j]

            ma = nanmean_np(c[-aaa:])
            self.ma_list.append(ma)
            if (len(self.ma_list) >= bbb) and (len(self.ma_list) >= ccc):
                ma_slope_15 = calculate_slope(np.array(self.ma_list[-bbb:]))
                ma_slope_60 = calculate_slope(np.array(self.ma_list[-ccc:]))
                ma_slope = ma_slope_15 + ma_slope_60
                self.ma_slope_list.append(ma_slope)

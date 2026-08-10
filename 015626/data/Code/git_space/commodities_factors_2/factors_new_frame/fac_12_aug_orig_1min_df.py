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


class fac_12_aug_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close']
        self.normalize_size = int(15 * self.bars / freq)
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']

        aaa = 6
        bbb = 75
        ccc = 3

        diff = c[aaa:] - c[:-aaa]
        sig = np.sign(diff[-1]) * nansum_np(diff[-bbb:] ** 2)
        self.sig_list.append(sig)
        sig = ema_1(np.array(self.sig_list[-(ccc * 4):]) + np.array(self.sig_list[-(ccc * 4) - 1:-1]), ccc * 4, 1 / (ccc + 1))
        return sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close']

        aaa = 6
        bbb = 75
        ccc = 3

        n = ccc * 4
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
            else:
                c = c_all[:-j]
            if len(c) > 1:
                diff = c[aaa:] - c[:-aaa]
                sig = np.sign(diff[-1]) * nansum_np(diff[-bbb:] ** 2)
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)

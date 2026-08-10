from rolling_adj import *

import numpy as np
from commodity_framework import FutureFactor


def replace_zero(x):
    if isinstance(x, float):
        if np.abs(x) < 1e-8:
            x = np.nan
    elif isinstance(x, np.ndarray):
        x = np.where(np.abs(x) < 1e-8, np.nan, x)
    else:
        raise TypeError(type(x))
    return x


def ema_archive(factor_array, d, alpha):
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    flag = np.isnan(factor_array) | np.isnan(weight)
    factor_array[flag] = np.nan
    weight[flag] = np.nan
    factor = nansum_np(factor_array[-d:] * weight) / nansum_np(weight)
    return factor


class fac_29_aug_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['high_secmain', 'low_secmain']
        self.normalize_size = 4800
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        h = data['high_secmain']
        l = data['low_secmain']

        aaa = 10
        bbb = 90

        h_diff = nanmean_np(h[-aaa:]) - nanmean_np(h[-aaa - 1:-1])
        l_diff = nanmean_np(l[-aaa:]) - nanmean_np(l[-aaa - 1:-1])
        sig = h_diff + l_diff
        self.sig_list.append(sig)
        sig = nanmean_np(np.array(self.sig_list[-8:])) + ema_1(np.array(self.sig_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1)) * 4
        return sig

    def pre_calculate(self, data):
        h_all = data['high_secmain']
        l_all = data['low_secmain']

        aaa = 10
        bbb = 90

        n = bbb * 3
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                h = h_all
                l = l_all
            else:
                h = h_all[:-j]
                l = l_all[:-j]

            h_diff = nanmean_np(h[-aaa:]) - nanmean_np(h[-aaa - 1:-1])
            l_diff = nanmean_np(l[-aaa:]) - nanmean_np(l[-aaa - 1:-1])
            sig = h_diff + l_diff
            self.sig_list.append(sig)

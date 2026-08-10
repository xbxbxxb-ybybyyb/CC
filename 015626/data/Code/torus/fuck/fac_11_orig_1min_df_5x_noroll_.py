from rolling_adj import *

import numpy as np
from commodity_framework import FutureFactor


def replace_zero(x):
    if isinstance(x, float):
        if np.abs(x) < 1e-8:
            x = np.nan
    elif isinstance(x, np.ndarray):
        x = np.where(np.abs(x) > 1e-8, x, np.nan)
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


class fac_11_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['close', 'high', 'low']
        self.normalize_size = int(1 * self.bars/ freq)
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']
        l = data['low']

        aaa = 375
        bbb = 375
        ccc = 14

        hh = nanmax_np(h[-aaa:])
        ll = nanmin_np(l[-bbb:])
        sig = 2 * c[-1] / replace_zero(hh + ll)
        self.sig_list.append(sig)
        sig = nanmean_np(np.array(self.sig_list[-ccc:])) + ema_1(np.array(self.sig_list[-(ccc * 2):]), ccc * 2, 1 / (int(ccc / 2) + 1))
        return sig

    def pre_calculate(self, data):
        c_all = data['close']
        h_all = data['high']
        l_all = data['low']

        aaa = 375
        bbb = 375
        ccc = 14

        n = ccc * 2
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                h = h_all
                l = l_all
            else:
                c = c_all[:-j]
                h = h_all[:-j]
                l = l_all[:-j]
            if len(c) > 1:
                hh = nanmax_np(h[-aaa:])
                ll = nanmin_np(l[-bbb:])
                sig = 2 * c[-1] / replace_zero(hh + ll)
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)

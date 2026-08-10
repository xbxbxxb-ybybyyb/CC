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


class fac_14_aug_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'high', 'low', 'tday']
        self.normalize_size = 10
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']
        l = data['low']
        t = data['tday']

        bbb = 10

        tday_h = nanmax_np(h[t == t[-1]])
        tday_l = nanmin_np(l[t == t[-1]])
        sig = -(tday_h - c[-1]) / replace_zero(tday_h - tday_l)
        self.sig_list.append(sig)
        sig = ema_1(np.array(self.sig_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        return sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close']
        h_all = data['high']
        l_all = data['low']
        t_all = data['tday']

        bbb = 10

        n = bbb * 3
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                h = h_all
                l = l_all
                t = t_all
            else:
                c = c_all[:-j]
                h = h_all[:-j]
                l = l_all[:-j]
                t = t_all[:-j]

            try:
                tday_h = nanmax_np(h[t == t[-1]])
                tday_l = nanmin_np(l[t == t[-1]])
                sig = -(tday_h - c[-1]) / replace_zero(tday_h - tday_l)
                self.sig_list.append(sig)
            except:
                self.sig_list.append(np.nan)

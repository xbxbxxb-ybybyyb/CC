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


class fac_13_aug_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'low']
        self.normalize_size = 5 * 300
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        l = data['low']

        aaa = 30
        bbb = 8

        ctl_r1 = nanmin_np(l[-aaa:]) / replace_zero(nanmean_np(l[-bbb:]))
        ctl_r2 = nanmin_np(c[-aaa:]) / replace_zero(nanmean_np(c[-bbb:]))
        sig = ctl_r1 + ctl_r2
        self.sig_list.append(sig)
        sig = ema_1(np.array(self.sig_list[-15:]), 15, 1 / 3)
        return -sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close']
        l_all = data['low']

        aaa = 30
        bbb = 8

        n = 20
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                l = l_all
            else:
                c = c_all[:-j]
                l = l_all[:-j]

            ctl_r1 = nanmin_np(l[-aaa:]) / replace_zero(nanmean_np(l[-bbb:]))
            ctl_r2 = nanmin_np(c[-aaa:]) / replace_zero(nanmean_np(c[-bbb:]))
            sig = ctl_r1 + ctl_r2
            self.sig_list.append(sig)

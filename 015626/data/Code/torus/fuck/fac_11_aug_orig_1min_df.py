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


class fac_11_aug_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'high', 'low']
        self.normalize_size = int(1 * self.bars / freq)
        self.normalize_type = 'ts_rank'

        self.sig2_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']
        l = data['low']

        aaa1 = 3
        bbb1 = 3
        aaa2 = 35
        bbb2 = 35
        ccc = 6

        hh = nanmax_np(h[-aaa1:])
        ll = nanmin_np(l[-bbb1:])
        sig1 = 2 * c[-1] / replace_zero(hh + ll)

        hh = nanmax_np(h[-aaa2:])
        ll = nanmin_np(l[-bbb2:])
        sig2 = 2 * c[-1] / replace_zero(hh + ll)
        self.sig2_list.append(sig2)
        sig2 = nanmean_np(np.array(self.sig2_list[-ccc:])) + ema_1(np.array(self.sig2_list[-(ccc * 2):]), ccc * 2, 1 / (int(ccc / 2) + 1))
        sig = sig2 - 4 * sig1
        return sig

    def pre_calculate(self, data):
        c_all = data['close']
        h_all = data['high']
        l_all = data['low']

        aaa2 = 35
        bbb2 = 35
        ccc = 6

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
                hh = nanmax_np(h[-aaa2:])
                ll = nanmin_np(l[-bbb2:])
                sig2 = 2 * c[-1] / replace_zero(hh + ll)
                self.sig2_list.append(sig2)
            else:
                self.sig2_list.append(np.nan)

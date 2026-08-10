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


def calculate_rwi(h, l, c, window):
    hl = h[1:] - l[1:]
    hc = np.abs(h[1:] - c[:-1])
    lc = np.abs(l[1:] - c[:-1])
    tr = nanmax_np([hl, hc, lc], axis=0)
    atr = nanmean_np(tr[-window:])
    rwi_h = (h[-1] - nanmin_np(l[-window:])) / replace_zero(atr)
    rwi_l = (nanmax_np(h[-window:]) - l[-1]) / replace_zero(atr)
    return rwi_h, rwi_l


class fac_1_df_10x_(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 10 * self.freq
        self.required_columns = ['close', 'high', 'low']
        self.normalize_size = int(20 * self.bars / self.freq)
        self.normalize_type = 'ts_rank'

        self.rwi_fac_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']
        l = data['low']

        aaa = 900
        bbb = 40

        rwi_h, rwi_l = calculate_rwi(h, l, c, aaa)
        rwi_fac = (rwi_h - rwi_l) / replace_zero(rwi_h + rwi_l)
        self.rwi_fac_list.append(rwi_fac)
        sig = nanmean_np(np.array(self.rwi_fac_list[-bbb:]))
        return sig

    def pre_calculate(self, data):
        c_all = data['close']
        h_all = data['high']
        l_all = data['low']

        aaa = 900

        n = 100
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

            if len(c) > 0:
                rwi_h, rwi_l = calculate_rwi(h, l, c, aaa)
                rwi_fac = (rwi_h - rwi_l) / replace_zero(rwi_h + rwi_l)
                self.rwi_fac_list.append(rwi_fac)
            else:
                self.rwi_fac_list.append(np.nan)

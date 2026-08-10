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


class fac_1_3_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'high', 'low']
        self.normalize_size = int(3 * self.bars / self.freq)
        self.normalize_type = 'ts_rank'

        self.rwi_fac2_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']
        l = data['low']

        aaa1 = 60
        aaa2 = 5
        bbb = 30

        rwi_h, rwi_l = calculate_rwi(h, l, c, aaa1)
        rwi_fac1 = (rwi_h - rwi_l) / replace_zero(rwi_h + rwi_l)

        rwi_h, rwi_l = calculate_rwi(h, l, c, aaa2)
        rwi_fac2 = (rwi_h - rwi_l) / replace_zero(rwi_h + rwi_l)
        self.rwi_fac2_list.append(rwi_fac2)
        rwi_fac2 = nanmean_np(np.array(self.rwi_fac2_list[-bbb:]))

        fac_raw = rwi_fac1 + rwi_fac2
        c_diff = c[1:] - c[:-1]
        vol = nanstd_np(c_diff[-60:], ddof=1)
        sig = fac_raw / replace_zero(vol)
        return sig

    def pre_calculate(self, data):
        self.rwi_fac2_list = []
        c_all = data['close']
        h_all = data['high']
        l_all = data['low']

        aaa2 = 5

        n = 30
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
                rwi_h, rwi_l = calculate_rwi(h, l, c, aaa2)
                rwi_fac2 = (rwi_h - rwi_l) / replace_zero(rwi_h + rwi_l)
                self.rwi_fac2_list.append(rwi_fac2)
            else:
                self.rwi_fac2_list.append(np.nan)

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


class fac_23_aug_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['close', 'open', 'high', 'low']
        self.normalize_size = 1 * 300
        self.normalize_type = 'ts_rank'

        self.vwtc_list = []

    def calculate(self, data):
        c = data['close']
        o = data['open']
        h = data['high']
        l = data['low']

        aaa = 10
        bbb = 10

        ho = nanmax_np(h[-aaa:]) - o[-1 - aaa]
        cl = c[-1] - nanmin_np(l[-aaa:])
        hl = (nanmax_np(h[-aaa:]) - nanmin_np(l[-aaa:])) * 2
        c_diff = c[1:] - c[:-1]
        vol = nanstd_np(c_diff[-(aaa * 2):], ddof=1)
        vwtc = ho * cl / replace_zero(hl) / replace_zero(vol)
        self.vwtc_list.append(vwtc)

        sig = ema_1(np.array(self.vwtc_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        return sig

    def pre_calculate(self, data):
        c_all = data['close']
        o_all = data['open']
        h_all = data['high']
        l_all = data['low']

        aaa = 10
        bbb = 10

        n = bbb * 3
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                o = o_all
                h = h_all
                l = l_all
            else:
                c = c_all[:-j]
                o = o_all[:-j]
                h = h_all[:-j]
                l = l_all[:-j]

            if len(c) > 1 + aaa:
                ho = nanmax_np(h[-aaa:]) - o[-1 - aaa]
                cl = c[-1] - nanmin_np(l[-aaa:])
                hl = (nanmax_np(h[-aaa:]) - nanmin_np(l[-aaa:])) * 2
                c_diff = c[1:] - c[:-1]
                vol = nanstd_np(c_diff[-(aaa * 2):], ddof=1)
                vwtc = ho * cl / replace_zero(hl) / replace_zero(vol)
                self.vwtc_list.append(vwtc)
            else:
                self.vwtc_list.append(np.nan)

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


class fac_30_orig_1min_df_5x_noroll_(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 5 * self.freq
        self.required_columns = ['close', 'low']
        self.normalize_size = 15000
        self.normalize_type = 'ts_rank'

        self.lm_list = []
        self.lltc_list = []

    def calculate(self, data):
        c = data['close']
        l = data['low']

        aaa = 600
        bbb = 120

        lm = nanmean_np(l[-5:])
        self.lm_list.append(lm)

        ll = nanmin_np(np.array(self.lm_list[-aaa:]))
        cc = ema_1(c[-15:], 15, 1 / 6)
        lltc = cc - ll
        self.lltc_list.append(lltc)

        sig = nanmean_np(np.array(self.lltc_list[-int(np.sqrt(bbb)):]))
        return sig

    def pre_calculate(self, data):
        c_all = data['close']
        l_all = data['low']

        aaa = 600
        bbb = 120

        n = aaa + bbb
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                l = l_all
            else:
                c = c_all[:-j]
                l = l_all[:-j]

            lm = nanmean_np(l[-5:])
            self.lm_list.append(lm)

            if len(self.lm_list) >= aaa:
                ll = nanmin_np(np.array(self.lm_list[-aaa:]))
                cc = ema_1(c[-15:], 15, 1 / 6)
                lltc = cc - ll
                self.lltc_list.append(lltc)
            else:
                self.lltc_list.append(np.nan)

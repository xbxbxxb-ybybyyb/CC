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


class fac_9_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['open', 'close', 'low']
        self.normalize_size = 300 * 6
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        o = data['open']
        c = data['close']
        l = data['low']

        aaa = 120
        bbb = 2

        twap = (o + c) / 2
        rtn = twap[45:] - twap[:-45]
        vol = nanstd_np(rtn[-aaa:], ddof=1)
        ret = c[-1] - nanmin_np(l[-aaa - 1:-1])
        sig = ret / replace_zero(vol)
        self.sig_list.append(sig)
        sig = ema_1(np.array(self.sig_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        return sig

    def pre_calculate(self, data):
        o_all = data['open']
        c_all = data['close']
        l_all = data['low']

        aaa = 120

        n = 10
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                o = o_all
                c = c_all
                l = l_all
            else:
                o = o_all[:-j]
                c = c_all[:-j]
                l = l_all[:-j]
            if len(c) > 1:
                twap = (o + c) / 2
                rtn = twap[45:] - twap[:-45]
                vol = nanstd_np(rtn[-aaa:], ddof=1)
                ret = c[-1] - nanmin_np(l[-aaa - 1:-1])
                sig = ret / replace_zero(vol)
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)

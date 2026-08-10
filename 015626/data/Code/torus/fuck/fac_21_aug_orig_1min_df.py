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


class fac_21_aug_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'open', 'high', 'low']
        self.normalize_size = 3 * 300
        self.normalize_type = 'ts_rank'

    def calculate(self, data):
        c = data['close']
        o = data['open']
        h = data['high']
        l = data['low']

        aaa = 8
        bbb = 20
        
        co = np.abs(c - o)
        co = np.where(co, co, 0.01)
        hl = h - l
        temp = hl / co
        ret = c[aaa:] - c[:-aaa]
        if len(ret[-(bbb * 3):]) != len(temp[-(bbb * 3):]):
            return np.nan
        sig = ema_1(temp[-(bbb * 3):] * ret[-(bbb * 3):], bbb * 3, 1 / (bbb + 1))
        return sig

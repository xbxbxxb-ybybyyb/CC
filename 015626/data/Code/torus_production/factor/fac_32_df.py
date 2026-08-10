from rolling_adj import *

import numpy as np
import bottleneck as bk
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

def calculate_rolling_norm(sig, window):
    sig_max = move_max_bk(sig, window=window, min_count=int(window / 2), axis=0)
    sig_min = move_min_bk(sig, window=window, min_count=int(window / 2), axis=0)
    temp = sig_max - sig_min
    temp[abs(temp) < 1e-8] = np.nan
    signal = (sig - sig_min) / temp
    return 2 * signal - 1


class fac_32_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close']
        self.normalize_size = int(15 * self.bars / self.freq)
        self.normalize_type = 'ts_rank'

    def calculate(self, data):
        c = data['close']

        aaa = 5
        bbb = 10
        coef = int(self.bars / self.freq)
        sig1 = calculate_rolling_norm(c, int(coef * aaa / 100))
        sig1 = nanmean_np(sig1[-bbb:])
        sig2 = calculate_rolling_norm(c, int(coef * aaa / 5))
        sig2 = ema_1(sig2[-(bbb * 3):], bbb * 3, 1 / (bbb + 1))

        c_diff = c[1:] - c[:-1]
        co = nanstd_np(c_diff[-bbb:], ddof=1)
        sig = (sig1 + sig2) / replace_zero(co)
        return sig

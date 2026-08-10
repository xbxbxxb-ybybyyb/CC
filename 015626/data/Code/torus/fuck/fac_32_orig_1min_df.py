import numpy as np
import bottleneck as bk
from commodity_framework import FutureFactor
from operators_cc_com import *
from rolling_adj import *


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
    if len(sig) > window:
        sig_max = move_max_bk(sig, window=window, min_count=int(window / 2), axis=0)
        sig_min = move_min_bk(sig, window=window, min_count=int(window / 2), axis=0)
    else:
        w2 = len(sig)
        sig_max = move_max_bk(sig, window=w2, min_count=int(w2 / 2), axis=0)
        sig_min = move_min_bk(sig, window=w2, min_count=int(w2 / 2), axis=0)
    temp = sig_max - sig_min
    temp[abs(temp) < 1e-8] = np.nan
    signal = (sig - sig_min) / temp
    return 2 * signal - 1


class fac_32_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close']
        self.normalize_size = 300
        self.normalize_type = 'ts_rank'

    def calculate(self, data):
        c = data['close']

        aaa = 120
        bbb = 5

        sig1 = calculate_rolling_norm(c, int(aaa / 4))
        sig1 = nanmean_np(sig1[-100:])
        sig2 = calculate_rolling_norm(c, aaa)
        sig2 = ema_1(sig2[-(bbb * 3):], bbb * 3, 1 / (bbb + 1))

        c_diff = c[1:] - c[:-1]
        co = nanstd_np(c_diff[-30:], ddof=1)
        sig = (sig1 + sig2) / replace_zero(co)
        return sig

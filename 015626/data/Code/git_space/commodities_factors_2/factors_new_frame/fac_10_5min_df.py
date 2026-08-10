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


def irr_filter(input_signal, window):
    alpha = 2 / (window + 1)
    b0 = alpha - (alpha ** 2) / 4
    b1 = (alpha ** 2) / 2
    b2 = -(alpha - (3 * alpha ** 2) / 4)
    a1 = -2 * (1 - alpha)
    a2 = (1 - alpha) ** 2
    y = np.zeros_like(input_signal)
    for n in range(len(input_signal)):
        if n == 0:
            y[n] = b0 * input_signal[n]
        elif n == 1:
            y[n] = b0 * input_signal[n] + b1 * input_signal[n - 1] - a1 * y[n - 1]
        else:
            y[n] = (b0 * input_signal[n] + b1 * input_signal[n - 1] + b2 * input_signal[n - 2] - a1 * y[n - 1] - a2 * y[n - 2])
    return y


class fac_10_5min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['close', 'high']
        self.normalize_size = int(5 * self.bars / freq)
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']

        aaa = int(self.bars / self.freq)
        bbb = 10

        rtn = c[1:] - c[:-1]
        vol1 = nanstd_np(rtn[-30:], ddof=1)
        vol2 = nanstd_np(rtn[-aaa:], ddof=1)
        ret1 = nanmax_np(h[-aaa - 1:-1]) - c[-1]
        ret2 = nanmax_np(h[-10 - 1:-1]) - c[-1]
        sig = (ret1 + ret2) / (replace_zero(vol1) * replace_zero(vol2))
        self.sig_list.append(sig)
        sig = sig + irr_filter(np.array(self.sig_list[-bbb:]), 2)[-1]
        return -sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close']
        h_all = data['high']

        aaa = int(self.bars / self.freq)
        bbb = 10

        n = bbb
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                h = h_all
            else:
                c = c_all[:-j]
                h = h_all[:-j]

            if len(c) > 1:
                rtn = c[1:] - c[:-1]
                vol1 = nanstd_np(rtn[-30:], ddof=1)
                vol2 = nanstd_np(rtn[-aaa:], ddof=1)
                ret1 = nanmax_np(h[-aaa - 1:-1]) - c[-1]
                ret2 = nanmax_np(h[-10 - 1:-1]) - c[-1]
                sig = (ret1 + ret2) / (replace_zero(vol1) * replace_zero(vol2))
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)


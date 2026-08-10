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


class fac_10_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['close', 'high']
        self.normalize_size = int(1 * self.bars / freq)
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']

        aaa = int(self.bars / self.freq)
        bbb = 5

        rtn = c[1:] - c[:-1]
        vol = nanstd_np(rtn[-30:], ddof=1)
        ret1 = nanmax_np(h[-aaa - 1:-1]) - c[-1]
        ret2 = nanmax_np(h[-10 - 1:-1]) - c[-1]
        sig = (ret1 + ret2) / replace_zero(vol)
        self.sig_list.append(sig)
        sig = sig + nanmean_np(np.array(self.sig_list[-bbb:]))
        return -sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close']
        h_all = data['high']

        aaa = int(self.bars / self.freq)
        bbb = 5

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
                vol = nanstd_np(rtn[-30:], ddof=1)
                ret1 = nanmax_np(h[-aaa - 1:-1]) - c[-1]
                ret2 = nanmax_np(h[-10 - 1:-1]) - c[-1]
                sig = (ret1 + ret2) / replace_zero(vol)
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)

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


class fac_10_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'high', 'dt']
        self.normalize_size = int(1 * self.bars / freq)
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']

        aaa = 200
        bbb = 10

        rtn = c[1:] - c[:-1]
        vol = nanstd_np(rtn[-aaa:], ddof=1)
        ret = nanmax_np(h[-aaa - 1:-1]) - c[-1]
        sig = ret / replace_zero(vol)
        self.sig_list.append(sig)
        sig = nanmean_np(np.array(self.sig_list[-bbb:]))
        return -sig

    def pre_calculate(self, data):
        c_all = data['close']
        h_all = data['high']

        aaa = 200
        bbb = 10

        n = bbb
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                h = h_all
                ddt = data['dt']
            else:
                c = c_all[:-j]
                h = h_all[:-j]
                ddt = data['dt'][:-j]
            if len(c) > 1:
                rtn = c[1:] - c[:-1]
                vol = nanstd_np(rtn[-aaa:], ddof=1)
                ret = nanmax_np(h[-aaa - 1:-1]) - c[-1]
                sig = ret / replace_zero(vol)
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)

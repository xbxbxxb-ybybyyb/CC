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


class fac_31_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close_secmain', 'high_secmain', 'low_secmain']
        self.normalize_size = int(2.5 * self.bars / self.freq)
        self.normalize_type = 'ts_rank'

        self.hh_list = []
        self.ll_list = []

    def calculate(self, data):
        c = data['close_secmain']
        h = data['high_secmain']
        l = data['low_secmain']

        aaa = int(self.bars / 3)
        bbb = 10

        hc = nanmax_np(h[-aaa:]) - c[-1]
        cl = c[-1] - nanmin_np(l[-aaa:])
        hl = nanmax_np(h[-aaa:]) - nanmin_np(l[-aaa:])
        hh = hc / replace_zero(hl)
        ll = cl / replace_zero(hl)
        self.hh_list.append(hh)
        self.ll_list.append(ll)
        vwtc = nanmean_np(np.array(self.ll_list[-bbb:])) - nanmean_np(np.array(self.hh_list[-bbb:]))

        c_diff = c[1:] - c[:-1]
        co = nanstd_np(c_diff[-int(self.bars / 10):], ddof=1)
        sig = vwtc / replace_zero(co) / replace_zero(np.sqrt(co))
        return sig

    def pre_calculate(self, data):
        self.hh_list = []
        self.ll_list = []
        c_all = data['close_secmain']
        h_all = data['high_secmain']
        l_all = data['low_secmain']

        aaa = int(self.bars / 3)
        bbb = 10

        n = bbb
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
            if len(c) > 1:
                hc = nanmax_np(h[-aaa:]) - c[-1]
                cl = c[-1] - nanmin_np(l[-aaa:])
                hl = nanmax_np(h[-aaa:]) - nanmin_np(l[-aaa:])
                hh = hc / replace_zero(hl)
                ll = cl / replace_zero(hl)
                self.hh_list.append(hh)
                self.ll_list.append(ll)
            else:
                self.hh_list.append(np.nan)
                self.ll_list.append(np.nan)
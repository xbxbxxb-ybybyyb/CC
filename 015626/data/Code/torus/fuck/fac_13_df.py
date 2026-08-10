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


class fac_13_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'low']
        self.normalize_size = 2 * 300
        self.normalize_type = 'ts_rank'

    def calculate(self, data):
        c = data['close']
        l = data['low']

        aaa = 15
        bbb = 3

        ctl_r1 = nanmin_np(l[-aaa:]) / replace_zero(nanmean_np(l[-bbb:]))
        ctl_r2 = nanmin_np(c[-aaa:]) / replace_zero(nanmean_np(c[-bbb:]))
        sig = ctl_r1 + ctl_r2
        return -sig

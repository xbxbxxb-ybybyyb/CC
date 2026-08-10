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


class fac_13_2_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'low']
        self.normalize_size = int(3 * self.bars / freq)
        self.normalize_type = 'ts_rank'

    def calculate(self, data):
        c = data['close']
        l = data['low']
        
        aaa = nanmax_np([int(10 / self.freq), 5])

        ctl_r1 = nanmax_np(l[-aaa:]) / replace_zero(l[-1])
        ctl_r1_shift1 = nanmax_np(l[-aaa - 1:-1]) / replace_zero(l[-2])
        ctl_r2 = nanmax_np(c[-20:]) / replace_zero(nanmean_np(c[-3:]))
        sig = (ctl_r1 + ctl_r1_shift1) / 2 + ctl_r2
        return -sig

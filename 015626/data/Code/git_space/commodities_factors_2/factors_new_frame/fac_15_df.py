from rolling_adj import *

import numpy as np
from commodity_framework import FutureFactor


class fac_15_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'tday']
        self.normalize_size = int(1 * self.bars / self.freq)
        self.normalize_type = 'ts_rank'

    def calculate(self, data):
        c = data['close']
        t = data['tday']

        tday_ma = nanmean_np(c[t == t[-1]])
        tday_ma2 = nanmean_np(c[t == t[-1]][-3:])
        sig = tday_ma2 - tday_ma
        return sig

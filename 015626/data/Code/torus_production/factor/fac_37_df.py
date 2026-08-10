from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





class fac_37_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.required_columns = ['close','volume']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 900

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 1

        

    def calculate(self, data):

        close = data['close'][-150:]

        volume = data['volume'][-150:]

        minute_ret = close[3:] - close[:-3]

        temp1 = nanmean_np(minute_ret[-120:])

        temp2 = nanmedian_np(minute_ret[-120:])

        temp = temp1 * 2 + temp2

        minute_ret_std = nanstd_np(minute_ret[-60:], ddof = 1)

        volume_sum = nansum_np(volume[-120:])

        if abs(minute_ret_std) < 1e-8:

            minute_ret_std = np.nan

        if abs(volume_sum) < 1e-8:

            volume_sum = np.nan

        factor = temp / minute_ret_std / volume_sum

        return factor
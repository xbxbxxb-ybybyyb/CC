from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

    

import numpy as np





class fac_39_long_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.required_columns = ['close','high']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 4500

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 3

        

    def calculate(self, data):

        aa = 600

        bb = 60

        

        close = data['close'][-610:]

        high = data['high'][-610:]

        rtn = close[1:] - close[:-1]

        vol = nanstd_np(rtn[-bb:], ddof = 1)

        if abs(vol) < 1e-8:

            vol = np.nan

        ret = close[-1] - nanmax_np(high[:-1][-aa:])

        factor = ret * vol

        return factor
from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

    

import numpy as np





class fac_39_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.required_columns = ['close_secmain','high_secmain']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 3000

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 1

        

    def calculate(self, data):

        aa = 210

        bb = 180

        close = data['close_secmain'][-220:]

        high = data['high_secmain'][-220:]

        rtn = close[1:] - close[:-1]

        vol = nanstd_np(rtn[-bb:], ddof = 1)

        if abs(vol) < 1e-8:

            vol = np.nan

        ret = close[-1] - nanmax_np(high[:-1][-aa:])

        factor = ret * vol

        return factor
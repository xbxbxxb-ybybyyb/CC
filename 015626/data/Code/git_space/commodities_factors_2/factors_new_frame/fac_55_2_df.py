from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np



class fac_55_2_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['low','close']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 5

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 5

        

        

    def calculate(self, data):

        low = data['low'][-1100:]

        close = data['close'][-1100:]

        

        hlow = move_min_bk(low,window = 90,min_count = 45)

        lltc_ind_r = close - hlow

        factor = ema_1(lltc_ind_r[-120:],120,1/41)

        return factor
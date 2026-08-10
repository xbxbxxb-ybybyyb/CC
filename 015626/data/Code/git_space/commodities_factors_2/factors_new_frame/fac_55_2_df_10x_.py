from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np



    

class fac_55_2_df_10x_(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['low','close']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 50

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 10

        

        

    def calculate(self, data):

        low = data['low'][-2200:]

        close = data['close'][-2200:]

        

        hlow = move_min_bk(low,window = 900,min_count = 450)

        lltc_ind_r = close - hlow

        factor = ema_1(lltc_ind_r[-1200:],1200,1/401)

        return factor

       
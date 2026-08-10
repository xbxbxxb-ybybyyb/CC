from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np




def ema_span_1(factor_array, d, span):

    return ema_1(factor_array, d = d, alpha=2 / (span + 1))



class fac_66_df(FutureFactor):

    def __init__(self, ticker, freq):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 11

        self.required_columns = ['close']

        self.normalize_size = int(self.bars_dict[ticker] * 5 / freq)

        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__       

    

    def calculate(self, data):

        coef = int(self.bars_dict[self.ticker] / self.freq)

        cls = data['close'][-11*coef:]

        pct = cls[1:]/cls[:-1]-1

        cls = cls[-160:]

        # calc unit

        short_window = 3

        long_window = 20

        vol_threshold = 8

        

        short_ma = move_mean_bk(cls,window=short_window,min_count=1)

        long_ma = move_mean_bk(cls,window=long_window,min_count=1) # need 25

        volatility = move_std_bk(pct,window = vol_threshold, min_count = 1,ddof = 1) # need 10   

        

        vol_median = move_median_bk(volatility,window = coef * 10, min_count = coef) 

        vol_id = volatility.copy()

        vol_id[volatility - vol_median < 1e-8] = 1

        vol_id[volatility - vol_median >= 1e-8] = 0



        short_ma = short_ma[-30:]

        long_ma = long_ma[-30:]

        vol_id = vol_id[-30:]

        ma_cross_distance = (short_ma - long_ma) / long_ma * vol_id

        factor = ema_span_1(ma_cross_distance,30,3)        

        return factor
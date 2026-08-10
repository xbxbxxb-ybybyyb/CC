from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





class fac_66_2_df(FutureFactor): 

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 1

        self.required_columns = ['close_secmain']

        self.normalize_size = 2000

        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__

        

    def calculate(self, data):

        cls = data['close_secmain'][-160:]

        pct = cls[1:]/cls[:-1]-1

        

        short_window = 3

        long_window = 20

        vol_threshold = 5

        

        short_ma = move_mean_bk(cls,window=short_window,min_count=1)

        long_ma = move_mean_bk(cls,window=long_window,min_count=1)

        volatility = move_std_bk(pct,window = vol_threshold, min_count = vol_threshold, ddof = 1)        

        vol_median = move_median_bk(volatility,window = 120,min_count = 60)

        vol_id = volatility.copy()

        vol_id[volatility - vol_median < 1e-8] = 1

        vol_id[volatility - vol_median >= 1e-8] = 0

        

        short_ma = short_ma[-5:]

        long_ma = long_ma[-5:]

        vol_id = vol_id[-5:]

        ma_cross_distance = (short_ma - long_ma) / long_ma * vol_id

        ma_cross_distance_mean = move_mean_bk(ma_cross_distance,window=5,min_count=1)

        factor = ma_cross_distance[-1] + ma_cross_distance_mean[-1]

        return  factor
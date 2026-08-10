from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np


    

class fac_55_orig_1min_df_5x_noroll_(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['low','close']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 1500

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 3       

        

    def calculate(self, data):

        low = data['low'][-610:]

        close = data['close'][-20:]

        low_mean = move_mean_bk(low,window = 5,min_count = 1)[-600:]

        flag = sum(np.isnan(low_mean))

        if flag > 300:

            hlow = np.nan

        else:

            hlow = nanmin_np(low_mean)

        hclose = ema_1(close[-15:],15,1/6)

        factor = hclose - hlow        

        return factor
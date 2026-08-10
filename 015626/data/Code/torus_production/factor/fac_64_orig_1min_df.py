from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





class fac_64_orig_1min_df(FutureFactor): 

    

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 2

        self.required_columns = ['close','high','low']

        self.normalize_size = 4000

        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__



    def calculate(self, data):

        spot_close = data['close'][-60:]

        spot_high = data['high'][-60:]

        spot_low = data['low'][-60:]

        cls_diff = np.abs(spot_close[1:] - spot_close[:-1])

        abs_distance = nansum_np(cls_diff[-20:])

        # calc factor1

        x_high = move_max_bk(spot_high, window = 45, min_count = 1)

        x_low = move_min_bk(spot_low, window = 45, min_count = 1)

        x = x_high - x_low

        x[abs(x) < 1e-8] = np.nan

        fac_raw1 = (2*spot_close - x_high - x_low)/x

        fac_raw1 = fac_raw1[-15:]

        weight1 = 1/6 * np.array([(1 - 1/6) ** i for i in range(15)])[::-1]

        factor1 = nansum_np(fac_raw1 * weight1) / nansum_np(weight1) # truncate_ema_1                

        

        # calc factor2

        x_high = move_max_bk(spot_high, window = 4, min_count = 1)

        x_low = move_min_bk(spot_low, window = 4, min_count = 1)

        x = x_high - x_low

        x[abs(x) < 1e-8] = np.nan

        fac_raw2 = (2*spot_close - x_high - x_low)/x

        fac_raw2 = fac_raw2[-15:]

        weight2 = 1/4 * np.array([(1 - 1/4) ** i for i in range(15)])[::-1]

        factor2 = nansum_np(fac_raw2 * weight2) / nansum_np(weight2) # truncate_ema_1        

        factor = (2*factor1 - factor2) / abs_distance        

        return factor
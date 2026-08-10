from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def chip_dis_array(price_array, volume_array):

    window = len(price_array)

    _r = nansum_np((price_array < price_array[-1]) * volume_array) / nansum_np(volume_array)

    return _r



class fast_fac_2_df(FutureFactor): 

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 1 # different product should be different

        self.required_columns = ['close','volume']

        self.normalize_size = 1500

        self.normalize_type = 'ts_rank'

    

    def calculate(self, data):

        v = data['volume']

        c = data['close']

        fac_raw1 = chip_dis_array(c[-90:],v[-90:]) * 8 - chip_dis_array(c[-2:],v[-2:])

        c_diff = c[1:] - c[:-1]

        vol = nanstd_np(c_diff[-15:], ddof = 1)

        factor = fac_raw1 * vol

        return factor
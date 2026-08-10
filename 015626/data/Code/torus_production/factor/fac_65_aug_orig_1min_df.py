from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





class fac_65_aug_orig_1min_df(FutureFactor): 

    def __init__(self,ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 1

        self.required_columns = ['close','volume']        

        self.normalize_size = 2000

        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__



    def calculate(self, data):

        cls = data['close'][-90:]

        vl = data['volume'][-90:]

        # calc vwap 10

        clsvl = cls * vl

        vwap_short = nansum_np(clsvl[-10:]) / nansum_np(vl[-10:])

        vwap_long = nansum_np(clsvl[-90:]) / nansum_np(vl[-90:])

        vwap_diff = vwap_short - vwap_long

        price_vol = nanstd_np(cls[-10:],ddof = 1)

        if abs(price_vol) < 1e-8:

            price_vol = np.nan

        factor = vwap_diff / price_vol

        return factor
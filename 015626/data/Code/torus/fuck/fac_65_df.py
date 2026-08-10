from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





class fac_65_df(FutureFactor): 

    

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        days_past = int(self.freq) * 1

        self.required_columns = ['close','volume','dt']

        self.normalize_size = int(self.bars_dict[ticker] * 2 / freq)

        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__        

    

    def calculate(self, data):

        cls = data['close'][-90:]

        vl = data['volume'][-90:]

        dtidx = data['dt'][-90:]

        # calc unit

        unit = self.freq

        short_window = nanmax_np([int(10 / unit), 3])

        long_window = nanmin_np([int(225 / unit / 3), 60])

        std_window = 15        

        # calc vwap 10

        clsvl = cls * vl

        vwap_short = nansum_np(clsvl[-short_window:]) / nansum_np(vl[-short_window:])

        vwap_long = nansum_np(clsvl[-long_window:]) / nansum_np(vl[-long_window:])

        vwap_diff = vwap_short - vwap_long

        price_vol = nanstd_np(cls[-std_window:],ddof = 1)

        if abs(price_vol) < 1e-8:

            price_vol = np.nan

        factor = vwap_diff / price_vol / price_vol / price_vol        

        return factor
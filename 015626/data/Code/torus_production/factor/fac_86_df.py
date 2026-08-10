from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





class fac_86_df(FutureFactor): 



    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 1 # different product should be different

        self.required_columns = ['close','sell_active']

        self.normalize_size = 1200

        self.normalize_type = 'ts_rank'

    

    def calculate(self, data):

        if 'zce' in self.ticker.lower():

            return 0



        bs = data['sell_active']

        cls = data['close']

        vol = nansum_np(bs[-30:])

        if abs(vol) < 1e-8:

            vol = np.nan

        bs_cls = (bs * cls)

        up = nansum_np(bs_cls[-30:]) / vol

        down = nanmean_np(bs[-30:])

        if abs(down) < 1e-8:

            down = np.nan

        factor = up / down

        return factor
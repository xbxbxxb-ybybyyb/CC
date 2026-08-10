from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np




class fac_68_orig_1min_df(FutureFactor): 

    

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 2

        self.required_columns = ['close','high']

        self.normalize_size = 5

        self.normalize_type = 'ts_rank'        

        self.factor_name = self.__class__.__name__

        self.hclose_list = []

        

    def calculate(self, data):

        cls = data['close'][-150:]

        high = data['high'][-150:]

        hlow_1 = move_mean_bk(high,window = 5, min_count = 1)

        hlow = move_min_bk(hlow_1,window=90,min_count=45)

        hclose = ema_1(cls[-15:],15,1/6)

        self.hclose_list.append(hclose)

        hclose_array = self.hclose_list[-45:]

        hlow_array = hlow[-45:]

        if len(hlow_array) < 45:
            dif = 45 - len(hlow_array)
            hlow_array = np.array([np.nan] * int(dif) + list(hlow_array))

        if len(hclose_array) < 45:
            dif = 45 - len(hclose_array)
            hclose_array = np.array([np.nan] * int(dif) + list(hclose_array))

        lltc_ind_r = (-(hlow_array-hclose_array))

        factor = ema_1(lltc_ind_r,45,1/16)

        return factor



    def pre_calculate(self,data):

        for i in range(45, -1, -1):

            if i == 0:

                cls_array = data['close'][-15:]

            else:

                cls_array = data['close'][-(15+i):-i]

            hclose = ema_1(cls_array,15,1/6)

            self.hclose_list.append(hclose)


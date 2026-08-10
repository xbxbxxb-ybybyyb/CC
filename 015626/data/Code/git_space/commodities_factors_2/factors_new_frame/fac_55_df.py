from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np



    

class fac_55_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['low','close']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 15

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 1

        self.prefactor_list = []

        

    def calculate(self, data):

        low = data['low'][-110:]

        close = data['close'][-20:]

        low_mean = move_mean_bk(low,window = 5,min_count = 1)[-100:]

        flag = sum(np.isnan(low_mean))

        if flag > 50:

            hlow = np.nan

        else:

            hlow = nanmin_np(low_mean)

        hclose = ema_1(close[-15:],15,1/6)

        prefactor = hclose - hlow

        self.prefactor_list.append(prefactor)

        factor = ema_1(self.prefactor_list[-30:],30,1/11)

        return factor



    def pre_calculate(self, data):
        self.prefactor_list = []

        for i in range(30, -1, -1):

            if i == 0:

                low = data['low'][-110:]

                close = data['close'][-20:]

            else:

                low = data['low'][-(110+i):-i]

                close = data['close'][-(20+i):-i]            
            if len(close) > 1:
                low_mean = move_mean_bk(low,window = 5,min_count = 1)[-100:]

                flag = sum(np.isnan(low_mean))

                if flag > 50:

                    hlow = np.nan

                else:

                    hlow = nanmin_np(low_mean)

                hclose = ema_1(close[-15:],15,1/6)

                prefactor = hclose - hlow

                self.prefactor_list.append(prefactor)
            else:
                self.prefactor_list.append(np.nan)

   
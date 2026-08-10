from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def ema_archive(factor_array,d,alpha):

    factor_array = np.array(factor_array)

    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]

    flag = np.isnan(factor_array) | np.isnan(weight)

    flag1 = np.sum(flag, axis=-1)  # 缺失值个数

    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)

    factor_array[flag] = np.nan

    weight[flag] = np.nan

    factor = nansum_np(factor_array[-d:] * weight) / nansum_np(weight) # truncate_ema_1

    return factor



def ema_span_1(factor_array, d, span):

    return ema_1(factor_array, d = d, alpha=2 / (span + 1))



class fac_68_orig_1min_df_20x_noroll_(FutureFactor): 



    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 5 # different product should be different

        self.required_columns = ['close','high']

        

        self.normalize_size = 50

        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__

        self.hclose_list = []

        #self.unit = 0

    

    def calculate(self, data):

        cls = data['close'][-1850:]

        high = data['high'][-1850:]

        hlow_1 = move_mean_bk(high,window = 5, min_count = 1)

        hlow = move_min_bk(hlow_1,window=1800,min_count=900)

        hclose = ema_1(cls[-15:],15,1/6)

        self.hclose_list.append(hclose)

        hclose_array = self.hclose_list[-450:]

        hlow_array = hlow[-450:]

        if len(hlow_array) < 450:
            dif = 450 - len(hlow_array)
            hlow_array = np.array([np.nan] * int(dif) + list(hlow_array))

        if len(hclose_array) < 450:
            dif = 450 - len(hclose_array)
            hclose_array = np.array([np.nan] * int(dif) + list(hclose_array))

        lltc_ind_r = (-(hlow_array-hclose_array))

        factor = ema_1(lltc_ind_r,450,1/151)

        return factor



    def pre_calculate(self,data):
        self.hclose_list = []

        for i in range(450, -1, -1):

            if i == 0:

                cls_array = data['close'][-15:]

            else:

                cls_array = data['close'][-(15+i):-i]

            hclose = ema_1(cls_array,15,1/6)

            self.hclose_list.append(hclose)


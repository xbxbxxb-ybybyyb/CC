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



class fac_68_orig_1min_df_10x_(FutureFactor): 

    



    def __init__(self, ticker, freq):
        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 7

        self.required_columns = ['close','high']

        self.normalize_size = 50

        self.normalize_type = 'ts_rank'

        

        self.factor_name = self.__class__.__name__
        self.hlow1_list = []
        self.hclose_list = []
        self.lltc_ind_r_list = []

    def calculate(self, data):
        aa = 900
        bbb = 150
        
        dhigh = data['high'][-5:]
        dclose = data['close'][-15:]

        
        hclose = ema_1(dclose, 15, 1/6)
        hlow1 = nanmean_np(dhigh)
        self.hlow1_list.append(hlow1)
        hlow = nanmin_np(self.hlow1_list[-aa:])
        lltc_ind_r = (-(hlow- (hclose)))
        self.lltc_ind_r_list.append(lltc_ind_r)
        factor = ema_1(self.lltc_ind_r_list[-bbb * 3:], bbb * 3, 1/(bbb + 1))

        return factor

    def pre_calculate(self,data):
        aa = 900
        bbb = 150
        
        for i in range(950, -1, -1):

            if i == 0:

                dhigh = data['high'][-5:]
                dclose = data['close'][-15:]

            else:

                dhigh = data['high'][-5 - i: -i]
                dclose = data['close'][-15 - i: -i]

            hclose = ema_1(dclose, 15, 1/6)
            hlow1 = nanmean_np(dhigh)
            self.hlow1_list.append(hlow1)
            hlow = nanmin_np(self.hlow1_list[-aa:])
            lltc_ind_r = (-(hlow- (hclose)))
            self.lltc_ind_r_list.append(lltc_ind_r)
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



class fast_fac_8_df(FutureFactor): 



    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 2

        self.required_columns = ['close','close_secmain']

        self.normalize_size = 600

        self.normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__

        

    def calculate(self, data):

        

        ret = data['close'][1:] - data['close'][:-1]

        ret_secmain = data['close_secmain'][1:] - data['close_secmain'][:-1]

        vol = move_std_bk(ret,window = 30, min_count = 1)

        vol0 = vol[-1]

        if abs(vol0) < 1e-8:

            vol0 = np.nan

        fac1 = ema_span_1(ret[-270:],270,75) / vol0

        fac2 = (ema_span_1(ret[-10:],10,3) - ema_span_1(ret_secmain[-10:],10,3)) / vol0

        factor = 2*fac1 - fac2

        return factor

        
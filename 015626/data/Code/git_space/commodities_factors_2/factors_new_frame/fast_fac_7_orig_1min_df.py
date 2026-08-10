from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def chip_dis_array(price_array, volume_array):

    window = len(price_array)

    _r = nansum_np((price_array < price_array[-1]) * volume_array) / nansum_np(volume_array)

    return _r



def cross_hub_num_array(data_array, d):

    # 过去一段时间曲线穿越中枢的次数

    data_centralized = data_array - move_mean_bk(data_array,window = d,min_count = int(d/2))

    flag = (data_centralized[1:] * data_centralized[:-1]) < 0

    output = np.sum(flag[-d:])

    return output 





class fast_fac_7_orig_1min_df(FutureFactor): 

    

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.ticker = ticker

        self.freq = freq

        self.days_past = int(freq) * 1 # different product should be different

        self.required_columns = ['close','volume']

        

        normalize_size = 150

        normalize_type = 'ts_rank'

        self.factor_name = self.__class__.__name__

        

    def calculate(self, data):

        close = data['close']

        volume = data['volume']  

        

        fac_raw = -chip_dis_array(close[-150:], volume[-150:]) + chip_dis_array(close[-4:], volume[-4:])

        fac_raw_1 = -chip_dis_array(close[-151:-1], volume[-151:-1]) + chip_dis_array(close[-5:-1], volume[-5:-1])        

        fac_raw1 = fac_raw * 6 + fac_raw_1        

        cls_diff = close[1:] - close[:-1]

        vol = nanstd_np(cls_diff[-30:],ddof=1)

        co = cross_hub_num_array(close,30) + 1

        if abs(vol) < 1e-8:

            vol = np.nan

        factor = -fac_raw1 / co / vol / vol

        return factor



    
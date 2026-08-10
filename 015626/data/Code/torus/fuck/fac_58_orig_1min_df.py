from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def cross_hub_num_array(data_array, d):

    # 过去一段时间曲线穿越中枢的次数

    data_centralized = data_array - move_mean_bk(data_array,window = d,min_count = int(d/2))

    flag = (data_centralized[1:] * data_centralized[:-1]) < 0

    output = np.sum(flag[-d:])

    return output

        

class fac_58_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['close_secmain', 'low_secmain', 'high_secmain', 'volume_secmain']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = int(self.bars_dict[ticker] / freq)

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 1

        

    def calculate(self, data):        

        close = data['close_secmain']

        high = data['high_secmain']

        low = data['low_secmain']

        volume = data['volume_secmain']

        # calc vwap sig

        mf = volume * close

        volume_sum = move_sum_bk(volume,window = 30, min_count = 15)

        mf_sum = move_sum_bk(mf, window = 30, min_count = 15)

        volume_sum[abs(volume_sum) < 1e-8] = np.nan

        vwap_val = mf_sum / volume_sum

        vwap_diff = close - vwap_val

        score_raw1 = nanmean_np(vwap_diff[-17:])

        co = cross_hub_num_array(close[-70:],30) / 5 + 1

        if abs(co) < 1e-8:

            co = np.nan

        factor = score_raw1 / co

        return factor
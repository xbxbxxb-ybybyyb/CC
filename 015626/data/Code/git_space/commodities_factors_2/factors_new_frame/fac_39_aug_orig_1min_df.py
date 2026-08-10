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

    

class fac_39_aug_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.required_columns = ['close_secmain','high_secmain']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 1500

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 3

        self.prefactor_list = []

        

    def calculate(self, data):

        aa = 35

        bb = 5

        close = data['close_secmain'][-150:]

        high = data['high_secmain'][-150:]

        rtn = close[1:] - close[:-1]

        vol = nanstd_np(rtn[-aa:], ddof = 1)

        if abs(vol) < 1e-8:

            vol = np.nan

        co = cross_hub_num_array(close[-130:], 60) + 1

        ret = close[-1] - nanmax_np(high[:-1][-aa:])

        prefactor = ret / vol / np.sqrt(co)

        self.prefactor_list.append(prefactor)

        factor = ema_1(self.prefactor_list[-bb*3:],bb*3,1/(bb+1))

        return factor



    def pre_calculate(self, data):
        self.prefactor_list = []

        aa = 35

        bb = 5

        for i in range(bb*3 + 5, -1, -1):

            if i == 0:

                close = data['close_secmain'][-150:]

                high = data['high_secmain'][-150:]

            else:

                close = data['close_secmain'][-(150+i):-i]

                high = data['high_secmain'][-(150+i):-i]
            if len(close) > 1:
                rtn = close[1:] - close[:-1]

                vol = nanstd_np(rtn[-aa:], ddof = 1)

                if abs(vol) < 1e-8:

                    vol = np.nan

                co = cross_hub_num_array(close[-130:], 60) + 1

                ret = close[-1] - nanmax_np(high[:-1][-aa:])

                prefactor = ret / vol / np.sqrt(co)

                self.prefactor_list.append(prefactor)
            else:
                self.prefactor_list.append(np.nan)

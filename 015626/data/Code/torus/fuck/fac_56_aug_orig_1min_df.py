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

    

def cross_hub_num_array(data_array, d):

    # 过去一段时间曲线穿越中枢的次数

    data_centralized = data_array - move_mean_bk(data_array,window = d,min_count = int(d/2))

    flag = (data_centralized[1:] * data_centralized[:-1]) < 0

    output = np.sum(flag[-d:])

    return output

    

class fac_56_aug_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['high','low','close']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 1200

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 1

        self.prefactor_list = []

        

    def calculate(self, data):

        aa = 15

        bb = 120

        ccc = 3

        bb_temp = 5

    

        high = data['high'][-150:]

        low = data['low'][-150:]

        close = data['close'][-150:]

        temp1 = nanmean_np(low[-aa:]) - nanmin_np(low[:-bb_temp][-(aa-bb_temp):])        

        temp2 = nanmean_np(high[-aa:]) - nanmax_np(high[:-bb_temp][-(aa-bb_temp):])

        temp = temp1 + temp2

        co = nanstd_np(close[-30:],ddof = 1)

        co2 = cross_hub_num_array(close[-(aa*2+10):],aa) + 1

        prefactor = temp * co / co2

        self.prefactor_list.append(prefactor)

        factor = prefactor + 1.2 * nanmean_np(self.prefactor_list[-10:])       

        return factor



    def pre_calculate(self, data):

        aa = 15

        bb = 120

        ccc = 3

        bb_temp = 5

        

        for i in range(6):

            if i == 0:

                high = data['high'][-150:]

                low = data['low'][-150:]

                close = data['close'][-150:]

            else:

                high = data['high'][-(150+i):-i]

                low = data['low'][-(150+i):-i]

                close = data['close'][-(150+i):-i]    

            temp1 = nanmean_np(low[-aa:]) - nanmin_np(low[:-bb_temp][-(aa-bb_temp):])        

            temp2 = nanmean_np(high[-aa:]) - nanmax_np(high[:-bb_temp][-(aa-bb_temp):])

            temp = temp1 + temp2

            co = nanstd_np(close[-30:],ddof = 1)

            co2 = cross_hub_num_array(close[-(aa*2+10):],aa) + 1

            prefactor = temp * co / co2

            self.prefactor_list.append(prefactor)   

        self.prefactor_list.reverse()
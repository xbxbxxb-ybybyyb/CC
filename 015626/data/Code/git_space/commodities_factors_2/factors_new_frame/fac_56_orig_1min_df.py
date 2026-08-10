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

    

class fac_56_orig_1min_df(FutureFactor):

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

        high = data['high'][-40:]

        low = data['low'][-40:]

        close = data['close'][-40:]

        temp1 = nanmean_np(low[-15:]) - nanmin_np(low[:-5][-10:])

        temp2 = nanmean_np(high[-15:]) - nanmax_np(high[:-5][-10:])

        temp = temp1 + temp2

        co = nanstd_np(close[-30:],ddof = 1)

        co2 = cross_hub_num_array(close[-40:],15) + 1        

        prefactor = temp * co / co2

        self.prefactor_list.append(prefactor)

        factor = ema_1(self.prefactor_list[-45:],45,1/16)

        return factor



    def pre_calculate(self, data):
        self.prefactor_list = []

        for i in range(45, -1, -1):

            if i == 0:

                high = data['high'][-40:]

                low = data['low'][-40:]

                close = data['close'][-40:]

            else:

                high = data['high'][-(40+i):-i]

                low = data['low'][-(40+i):-i]

                close = data['close'][-(40+i):-i]    

            temp1 = nanmean_np(low[-15:]) - nanmin_np(low[:-5][-10:])

            temp2 = nanmean_np(high[-15:]) - nanmax_np(high[:-5][-10:])

            temp = temp1 + temp2

            co = nanstd_np(close[-30:],ddof = 1)

            co2 = cross_hub_num_array(close[-40:],15) + 1        

            prefactor = temp * co / co2

            self.prefactor_list.append(prefactor)   


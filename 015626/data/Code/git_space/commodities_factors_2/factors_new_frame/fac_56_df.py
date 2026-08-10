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

    

class fac_56_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.factor_name = self.__class__.__name__

        self.required_columns = ['high','low','close']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = int(self.bars_dict[ticker]/freq * 2)

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 1

        self.prefactor_list = []

        

    def calculate(self, data):

        aa = int(15 / self.freq)

        bb_temp = int(5 / self.freq)

        ccc = 2

    

        high = data['high'][-40:]

        low = data['low'][-40:]

        close = data['close'][-40:]

        temp1 = nanmean_np(low[-aa:]) - nanmin_np(low[:-bb_temp][-(aa-bb_temp):])        

        temp2 = nanmean_np(high[-aa:]) - nanmax_np(high[:-bb_temp][-(aa-bb_temp):])

        temp = temp1 + temp2

        self.prefactor_list.append(temp)        

        co2 = cross_hub_num_array(low[-(aa*2+10):],aa) + 1

        factor = ema_1(self.prefactor_list[-ccc*3:],ccc*3,1/(ccc+1)) / co2        

        return factor



    def pre_calculate(self, data):
        self.prefactor_list = []

        aa = int(15 / self.freq)

        bb_temp = int(5 / self.freq)

        ccc = 2

        

        for i in range(6, -1, -1):

            if i == 0:

                high = data['high'][-40:]

                low = data['low'][-40:]

                close = data['close'][-40:]

            else:

                high = data['high'][-(40+i):-i]

                low = data['low'][-(40+i):-i]

                close = data['close'][-(40+i):-i]    

            temp1 = nanmean_np(low[-aa:]) - nanmin_np(low[:-bb_temp][bb_temp-aa:])

            temp2 = nanmean_np(high[-aa:]) - nanmax_np(high[:-bb_temp][bb_temp-aa:])

            temp = temp1 + temp2

            self.prefactor_list.append(temp)   

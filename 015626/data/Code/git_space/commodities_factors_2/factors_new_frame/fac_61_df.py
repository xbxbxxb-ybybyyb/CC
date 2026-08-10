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
    
class fac_61_df(FutureFactor):
    def __init__(self, ticker, freq = 1):
        super().__init__()
        self.factor_name = self.__class__.__name__
        self.required_columns = ['close_secmain','open_secmain']
        self.normalize_size = 900
        self.normalize_type = 'ts_rank'
        self.ticker = ticker
        self.freq = freq
        self.days_past = int(freq) * 1 # different product should be different
        self.prefactor_list = []
        
    def calculate(self, data):
        cls = data['close_secmain']
        opn = data['open_secmain']
        
        cdo_r = nanmean_np(cls[-4:]) - nanmean_np(opn[-4:])
        co = cross_hub_num_array(cls[-40:],15) + 1
        tmp_factor = cdo_r / co
        self.prefactor_list.append(tmp_factor)
        factor = ema_1(self.prefactor_list[-60:], 20 * 3, 1/(20 + 1))
        return factor

    def pre_calculate(self, data):
        self.prefactor_list = []
        for i in range(60, -1, -1):
            if i == 0:
                cls = data['close_secmain'][-40:]
                opn = data['open_secmain'][-10:]
            else:
                cls = data['close_secmain'][-(40+i):-i]
                opn = data['open_secmain'][-(10+i):-i]
            cdo_r = nanmean_np(cls[-4:]) - nanmean_np(opn[-4:])
            co = cross_hub_num_array(cls[-40:],15) + 1
            tmp_factor = cdo_r / co
            self.prefactor_list.append(tmp_factor)

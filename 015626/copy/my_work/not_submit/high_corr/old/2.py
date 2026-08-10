import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from help_functions_wsc import *



class 2_if(FactorGeneratorComplex):
    def __init__(self):
        super(2_if, self).__init__(required_columns = ['close_hs300', 'weight_hs300'],
                                   lookback_bars = 1500)

    def on_bar(self, data):
        # arron_os指标区间为[-100, 100]，100表示股价创新高，-100表示创新低，指标值越大，表示股价最近位置越高
        close = data['close_hs300']
        n = 20
        arron_up = ts_argmax(close, n) / n * 100  # 过去n天最高价出现时间与当前时间的距离占时间段长度的比例
        arron_down = ts_argmin(close, n) / n * 100  # 过去n天最低价出现时间与当前时间的距离占时间段长度的比例
        arron_os = arron_up - arron_down
        factor_init = arron_os

        factor_raw = (factor_init*data_dict['weight_hs300']).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 60)
        factor = ts_rank(factor_mean, 1200)

        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        #factor[factor <= -0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor


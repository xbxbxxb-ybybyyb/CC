import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc19_cfg_as(FactorGeneratorComplex):
    def __init__(self):
        super(wsc19_cfg_as, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_zz500']
        bool_mask = data['weight_boolean_zz500']
        amount_mask = stk_amount[bool_mask]

        # arron_os指标区间为[-100, 100]，100表示股价创新高，-100表示创新低，指标值越大，表示股价最近位置越高
        close = data['close_zz500']
        n = 30
        arron_up = ts_argmax(close, n) / n * 100  # 过去n分钟最高价出现时间与当前时间的距离占时间段长度的比例
        arron_down = ts_argmin(close, n) / n * 100  # 过去n分钟最低价出现时间与当前时间的距离占时间段长度的比例
        arron_os = arron_up - arron_down
        factor_init = arron_os


        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 18)
        factor = ts_rank(factor_mean, 1000)
        
        factor = factor.to_frame() 
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= -0.64] = 0
        #factor[factor>=0.5] = np.nan
        return factor
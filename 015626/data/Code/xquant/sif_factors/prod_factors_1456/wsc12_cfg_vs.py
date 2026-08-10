import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc12_cfg_vs(FactorGeneratorComplex):
    def __init__(self):
        super(wsc12_cfg_vs, self).__init__(required_columns=['close_zz500', 'high_zz500', 'low_zz500', 'open_zz500', 'stk_volatility_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']

        # 东方金工20200421，通过股价在回滚区间内的位置衡量股票日内买卖压力
        stk_close = data['close_zz500']
        stk_high = data['high_zz500']
        stk_low = data['low_zz500']
        stk_open = data['open_zz500']
        stk_price = (stk_high + stk_low + stk_open + stk_close) / 4
        n = 30
        rpp = ts_sum(stk_price, n)
        high_n = ts_max(stk_high, n)
        low_n = ts_min(stk_low, n)
        temp = high_n - low_n
        temp[abs(temp)<1e-8] = np.nan
        arpp = (rpp - low_n) / temp
        factor_init = -arpp
        
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 35)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>0] = 0
        return factor

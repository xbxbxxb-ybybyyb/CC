import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc10_cfg_vs(FactorGeneratorComplex):
    def __init__(self):
        super(wsc10_cfg_vs, self).__init__(required_columns=['close_zz500', 'stk_volatility_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data):
        # mask
        volatility_mask = data['stk_volatility_zz500']

        # 计算长短期收益率之差
        stk_close = data['close_zz500']
        stk_ret_short = stk_close.pct_change(10, fill_method=None)
        stk_ret_long = stk_close.pct_change(130, fill_method=None) 
        a = stk_ret_long - stk_ret_short
        a[a<0] = 0
        factor_init = a
        
        factor_raw = (factor_init * volatility_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 1)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor

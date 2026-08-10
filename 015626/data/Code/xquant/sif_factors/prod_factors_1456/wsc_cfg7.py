import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg7(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg7, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # 长短期收益率之差
        stk_close = data['close_zz500']
        stk_ret_short = stk_close.pct_change(15, fill_method=None)
        stk_ret_long = stk_close.pct_change(120, fill_method=None) 
        a = stk_ret_long - stk_ret_short
        a[a<0] = 0
        #a[a>0] = 1
        factor = (a * data['weight_zz500']).sum(axis=1)
        #factor = factor.rolling(5, min_periods=2).mean()

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 500)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor

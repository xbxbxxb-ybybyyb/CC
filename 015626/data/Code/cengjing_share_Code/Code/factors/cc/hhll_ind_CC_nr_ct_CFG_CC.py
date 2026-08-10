# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:55:29 2020

@author: appadmin
"""

import pandas as pd
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class hhll_ind_CC_nr_ct_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'close_spot', 'weight_boolean_zz500', 'turnover_zz500', 'high_zz500', 'low_zz500']
        super(hhll_ind_CC_nr_ct_CFG_CC, self).__init__(required_columns=required_columns
                                  )


    def on_bar(self, data):
        stk_close = data['close_zz500']
        index_close = data['close_spot']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_zz500']]
        turnover = (data['turnover_zz500'].rolling(60, min_periods = 15).mean())[data['weight_boolean_zz500']]
        temp1 = (data['high_zz500']>data['high_zz500'].shift(1)).astype(int)
        temp2 = (data['low_zz500']>data['low_zz500'].shift(1)).astype(int)
        
        temp =  temp1+temp2
        temp[temp==2] = 4
        factor = temp
        factor = rolling_norm(factor)
        #factor[abs(factor)>1] = np.nan
        tempp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        tempp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        mask = tempp2 * tempp4
        factor1 = (factor * mask).sum(axis = 1).to_frame()
        factor1 = factor1.rolling(30, min_periods = 15).mean()
        factor1 = ts_rank(factor1)
        factor1.columns = [self.__class__.__name__]
        return factor1
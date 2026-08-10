# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 14:46:59 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class L123_nr_ac_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300', 'close_spot_if', 'close_hs300', 'weight_boolean_hs300', 'low_hs300']
        super(L123_nr_ac_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        stk_close = data['close_hs300']
        index_close = data['close_spot_if']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        index_ret = index_close.pct_change(1, fill_method=None)
        stk_index_corr = stk_ret.rolling(1200, min_periods=600).corr(index_ret)
        stk_index_corr = stk_index_corr.replace([-np.inf, np.inf], np.nan)
        stk_index_corr = stk_index_corr[data['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp2 = stk_index_corr.gt(pd.Series(stk_index_corr.quantile(0.80, axis = 1)), axis=0)
        mask = temp1*temp2
        
        hlow = data['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)
        #i2[np.abs(i2)>1] = np.nan
        tempdf = (i2*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(45, min_periods = 23).mean()
        factor = ts_rank(factor)
        
        factor.columns = [self.__class__.__name__]
        return factor
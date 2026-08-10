# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 13:32:45 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class L123_nr_vt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'close_hs300', 'low_hs300',]
        super(L123_nr_vt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, df):
        stk_close = df['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[df['weight_boolean_hs300']]
        turnover = (df['turnover_hs300'].rolling(60, min_periods = 15).mean())[df['weight_boolean_hs300']]
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)    
        mask = temp3*temp4
        
        hlow = df['low_hs300']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        ctl_r = (i11-i12)
        ctl_r = rolling_norm(ctl_r, 242*5)
        ctl_r[np.abs(ctl_r)>1] = np.nan
        tempdf = (ctl_r*mask)
        tempdf = tempdf.mean(axis = 1).to_frame()
        factor = tempdf.rolling(40, min_periods = 2).mean()
        factor = ts_rank(factor, 720)
        
        factor.columns = [self.__class__.__name__]
        return factor
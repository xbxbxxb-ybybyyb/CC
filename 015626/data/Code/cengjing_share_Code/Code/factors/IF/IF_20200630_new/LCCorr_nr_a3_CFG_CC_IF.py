# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 09:45:43 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class LCCorr_nr_a3_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'close_hs300', 'low_hs300', 'amount_hs300']

        super(LCCorr_nr_a3_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

   
    def on_bar(self, df):
        
        df_s = (df['amount_hs300'].rolling(120, min_periods = 15).sum())[df['weight_boolean_hs300']]
        ret = (df['close_hs300']/df['close_hs300'].shift(30)-1)[df['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp6 = ret.gt(pd.Series(ret.quantile(0.80, axis = 1)), axis=0)       
        mask = temp1*temp6
        
        high = df['low_hs300']
        close = df['close_hs300']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_chgpcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)
        t_chgpcor2 = rolling_norm(t_chgpcor2)
        tempdf = (t_chgpcor2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(15, min_periods = 15).mean()
        factor = ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor
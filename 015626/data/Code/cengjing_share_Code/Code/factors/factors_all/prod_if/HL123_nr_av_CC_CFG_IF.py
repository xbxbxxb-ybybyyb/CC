# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:57:11 2020

@author: appadmin
"""

import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex

class HL123_nr_av_CC_CFG_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_hs300', 'amount_hs300', 'close_hs300', 'high_hs300', 'low_hs300']

        super(HL123_nr_av_CC_CFG_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

  
    def on_bar(self, data):
        df_s = (data['amount_hs300'].rolling(120, min_periods = 15).sum())[data['weight_boolean_hs300']]
        stk_close = data['close_hs300']
        stk_ret = stk_close.pct_change(1, fill_method=None)
        stk_volatility = ts_std(stk_ret, 30)
        stk_volatility = stk_volatility[data['weight_boolean_hs300']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)
        temp3 = stk_volatility.gt(pd.Series(stk_volatility.quantile(0.80, axis = 1)), axis=0)
        mask = temp3*temp1
        hlow = data['low_hs300']
        hhigh = data['high_hs300']
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12)
        i2 = rolling_norm(i2, 242*5)
        tempdf = (i2*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(30, min_periods = 15).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
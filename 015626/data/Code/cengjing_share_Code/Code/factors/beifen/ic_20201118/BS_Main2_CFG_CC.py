# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 09:44:35 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class BS_Main2_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_500', 'weight_500', 'BuyUniqueOrderNum_500', 'SellUniqueOrderNum_500', 'close_500']
        super(BS_Main2_CFG_CC, self).__init__(required_columns=required_columns
                                  )
    
    def on_bar(self, data):
        df_s = data['amount_500'].rolling(10, min_periods = 5).sum()
        df_s = df_s[data['weight_500']>0]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)

        factor = (data['SellUniqueOrderNum_500']+data['BuyUniqueOrderNum_500']).rolling(40, min_periods = 1).sum()*(data['close_500']/data['close_500'].shift(40)-1)
        factor = (factor[bool_df]).mean(axis = 1)
        #factor = factor.rolling(5, min_periods = 1).sum()
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]

        return factor
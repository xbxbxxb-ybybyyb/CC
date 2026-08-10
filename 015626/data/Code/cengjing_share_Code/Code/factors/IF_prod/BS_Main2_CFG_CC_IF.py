# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:45:03 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class BS_Main2_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_300', 'weight_300', 'BuyUniqueOrderNum_300', 'SellUniqueOrderNum_300', 'close_300']
        super(BS_Main2_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    def on_bar(self, data):
        df_s = data['amount_300'].rolling(10, min_periods = 5).sum()
        df_s = df_s[data['weight_300']>0]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)

        factor = (data['SellUniqueOrderNum_300']+data['BuyUniqueOrderNum_300']).rolling(40, min_periods = 1).sum()*(data['close_300']/data['close_300'].shift(40)-1)
        factor = (factor[bool_df]).mean(axis = 1)
        factor = factor.rolling(2, min_periods = 1).sum()
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]
        factor[factor<-0] = 0
        return factor
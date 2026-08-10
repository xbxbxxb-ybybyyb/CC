# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 13:13:40 2020

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class BS_Main_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_500', 'weight_500', 'BuyUniqueOrderNum_500', 'BuyTradeNum_500', 'SellUniqueOrderNum_500', 'SellTradeNum_500']
        super(BS_Main_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):
        df_s = data['amount_500'].rolling(10, min_periods = 5).sum()
        df_s = df_s[data['weight_500']>0]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)

        factor = (data['BuyUniqueOrderNum_500'] / data['BuyTradeNum_500']) - (data['SellUniqueOrderNum_500'] / data['SellTradeNum_500'])
        factor = (factor[bool_df]).mean(axis = 1)
        factor = factor.rolling(6, min_periods = 3).mean()
        factor = ts_rank(factor.to_frame())
        factor.columns = [self.__class__.__name__]

        return -factor
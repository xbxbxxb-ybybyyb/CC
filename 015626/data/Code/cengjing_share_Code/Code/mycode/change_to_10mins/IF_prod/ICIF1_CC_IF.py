# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 10:18:10 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

from factor_generator import FactorGenerator


class ICIF1_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns =['close', 'recent_month_mask']

        super(ICIF1_CC_IF, self).__init__(
                                  required_columns=required_columns)
        

    

    
    def on_bar(self, data):
        temp5 = data['close'].rolling(5, min_periods = 2).mean()
        temp10 = data['close'].rolling(10, min_periods = 5).mean()
        temp20 = data['close'].rolling(20, min_periods = 10).mean()
        temp60 = data['close'].rolling(60, min_periods = 30).mean()
        temp120 = data['close'].rolling(120, min_periods = 60).mean()
        temp5_diff = (temp5.diff()>0).astype(int)
        temp10_diff = (temp10.diff()>0).astype(int)
        temp20_diff = (temp20.diff()>0).astype(int)
        temp60_diff = (temp60.diff()>0).astype(int)
        temp120_diff = (temp120.diff()>0).astype(int)
        temp = (temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff).rolling(15, min_periods = 5).mean()
        factor = ts_rank(temp[data['recent_month_mask']].mean(axis = 1).to_frame())
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(10, min_periods = 2).mean()
        factor.columns = [self.__class__.__name__]
        return factor
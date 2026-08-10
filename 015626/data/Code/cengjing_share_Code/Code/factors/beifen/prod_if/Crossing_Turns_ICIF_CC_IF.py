# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 15:07:04 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class Crossing_Turns_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['open', 'low', 'close', 'high', 'vwap','recent_month_mask']

        super(Crossing_Turns_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)
    

    
    def on_bar(self, data):

        temp = np.abs(pd.DataFrame(np.where(data['open']-data['close'] == 0, 0.1, data['open']-data['close'])))
        temp.index = data['open'].index
        temp.columns = data['open'].columns
        temp0 = (data['high'] - data['low'])

        temp1 = temp0/temp
        temp1 = temp1.replace([-np.inf, np.inf], np.nan)
        a = (data['vwap']/data['vwap'].shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a)).rolling(25, min_periods = 5).mean()
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 242*3)
        factor = factor.rolling(2, min_periods = 2).mean()
        factor[factor<=-0.5]=np.nan
        factor = ts_rank(factor)
        factor[factor<=-0.5]=0
        return factor

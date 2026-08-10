# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 09:46:19 2020

@author: appadmin
"""
from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd
import numpy as np

class LRS_max_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['vwap', 'recent_month_mask']
 
        super(LRS_max_CC_IF, self).__init__(
                                  required_columns=required_columns)
        
    def on_bar(self, data):
        #448_LINEARREG_SLOPE(ts_max(twap, 40), 50)
        columnname = self.__class__.__name__
        temp1 = data['vwap'].rolling(50, min_periods = 20).max()
        holder = {}
        for item in temp1.columns:
            close_spot = (temp1[item]).values
            x = np.array(range(len(data['vwap'][item])))
            #print(item)
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 50))

        temp = pd.DataFrame(holder)
        temp.index = data['vwap'].index
        

        temp = (temp[data['recent_month_mask']]).mean(axis = 1)
        
        cc3 = ts_rank(temp.to_frame(), 500)
        cc3.columns = [columnname]
        return cc3
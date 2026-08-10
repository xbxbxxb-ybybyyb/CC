# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 11:15:57 2020

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG29_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_hs300', 'weight_boolean_hs300', 'close_hs300']

        super(CFG29_CC_IF, self).__init__(required_columns=required_columns)
        
    def on_bar(self, data):

         #448_LINEARREG_SLOPE(ts_max(twap, 40), 50)
        columnname = self.__class__.__name__
        temp1 = data['close_hs300'].rolling(35, min_periods = 20).max()
        holder = {}
        for item in temp1.columns:
            close_spot = (temp1[item]).values
            x = np.array(range(len(data['close_hs300'][item])))
            #print(item)
            holder[item] = pd.Series(rolling_linear_reg(x, close_spot, 35))

        temp = pd.DataFrame(holder)
        temp.index = data['close_hs300'].index
        

        temp = (temp[data['weight_boolean_hs300']]).mean(axis = 1)
        cc3 = ts_rank(temp.to_frame(), 400)
        cc3.columns = [columnname]

        return cc3
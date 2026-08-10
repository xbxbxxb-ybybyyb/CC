# -*- coding: utf-8 -*-
"""
Created on Thu May 20 10:55:53 2021

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class Short_CrossingTurns_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_zz500', 'close_zz500', 'low_zz500', 'open_zz500', 'weight_zz500']

        super(Short_CrossingTurns_CFG_CC, self).__init__(required_columns=required_columns
                                  )



    def on_bar(self, data):

        temp = np.abs(data['close_zz500']-data['open_zz500'])
        temp[abs(temp)<=1e-8] = 0.01
        #temp.index = hclose.index
        temp0 = (data['high_zz500'] - data['low_zz500'])
        temp1 = temp0/temp
        a = (data['close_zz500']/data['close_zz500'].shift(1)-1).rolling(30, min_periods = 15).sum()
        vwtc_r = (temp1*(a))#.rolling(2, min_periods = 1).mean()
        factor = (vwtc_r*data['weight_zz500']).mean(axis = 1)
        factor.index = data['close_zz500'].index
        factor = ts_rank(factor.to_frame())

        #factor = (factor - 0.25)*4/3
        factor.columns = [self.__class__.__name__]
 
        return factor


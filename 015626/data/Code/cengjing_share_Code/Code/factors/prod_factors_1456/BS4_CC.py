# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 17:53:22 2020

@author: appadmin
"""
from operators_cc import *
import numpy as np
from factor_generator_complex import FactorGeneratorComplex

class BS4_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['Bid1AmtMean_500', 'BuyNumOrdersSumMean_500', 'weight_500']

        super(BS4_CC, self).__init__(required_columns=required_columns)
        
    def on_bar(self, data):
        # ts_max(div(VolumeMean, position), 60).
        columnname = self.__class__.__name__
        temp1 = (data['Bid1AmtMean_500']/data['BuyNumOrdersSumMean_500']).rolling(10, min_periods = 5).mean()
        temp1[abs(temp1)>10000] = np.nan
        temp = (temp1*data['weight_500']).mean(axis = 1).to_frame()
        a2 = rolling_norm(temp, method = 'ts_rank')
        #a2.iloc[:, 0] = a2.iloc[:, 0].rolling(3, min_periods = 2).mean()
        a2.columns = [columnname]

        return a2

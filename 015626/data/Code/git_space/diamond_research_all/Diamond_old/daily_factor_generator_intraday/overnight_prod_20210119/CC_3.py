# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:25:04 2020

@author: appadmin
"""
from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd

class CC_3(FactorGenerator):
    def __init__(self):

        required_columns =['vwap', 'recent_month_mask']
 
        super(CC_3, self).__init__(required_columns=required_columns)
    
    def on_bar(self, data):
        temp_wp = (data['vwap'][data['recent_month_mask']]).between_time('9:30', '14:49')
        temp_wp = temp_wp.groupby(temp_wp.index.date)
        temp1 = ((temp_wp.max()-temp_wp.min())/temp_wp.min()).mean(axis = 1)
        a2 = ts_rank(temp1.to_frame(), 60)
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:33:19 2020

@author: appadmin
"""

from factor_generator import FactorGenerator
from operators_cc import *


class CC_7_if(FactorGenerator):
    def __init__(self, *args, **kwargs):

        required_columns =['high_if', 'low_if', 'recent_month_mask']
 
        super().__init__(*args, required_columns=required_columns, **kwargs)
        
    def on_bar(self, data):
        temp_high_if = (data['high_if'][data['recent_month_mask']]).between_time('14:00', '14:49')
        temp_high_if = temp_high_if.groupby(temp_high_if.index.date)
        temp_low_if = (data['low_if'][data['recent_month_mask']]).between_time('14:00', '14:49')
        temp_low_if = temp_low_if.groupby(temp_low_if.index.date)
        temp1 = ((temp_high_if.max()-temp_low_if.min())/temp_low_if.min()).mean(axis = 1)
        a2 = ts_rank(temp1.to_frame(), 30)
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
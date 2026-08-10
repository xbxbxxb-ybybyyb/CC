# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:34:56 2020

@author: appadmin
"""


from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd

class CC_8(FactorGenerator):
    def __init__(self):

        required_columns =['amount', 'recent_month_mask']
 
        super(CC_8, self).__init__(required_columns=required_columns)
    
    def on_bar(self, data):
        temp_amount = (data['amount'][data['recent_month_mask']]).between_time('9:30', '14:49')
        temp_amount = temp_amount.groupby(temp_amount.index.date)
        temp_amount_wp = (data['amount'][data['recent_month_mask']]).between_time('14:30', '14:49')
        temp_amount_wp = temp_amount_wp.groupby(temp_amount_wp.index.date)
        temp1 = (temp_amount_wp.mean()-temp_amount.mean()).mean(axis = 1)
        a2 = ts_rank(temp1.to_frame(), 60)
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:33:19 2020

@author: appadmin
"""

from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd

class CC_7(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'recent_month_mask']
 
        super(CC_7, self).__init__(
                                  required_columns=required_columns)
    def on_bar(self, data):
        temp_high = (data['high'][data['recent_month_mask']]).between_time('14:00', '14:49')
        temp_high = temp_high.groupby(temp_high.index.date)
        temp_low = (data['low'][data['recent_month_mask']]).between_time('14:00', '14:49')
        temp_low = temp_low.groupby(temp_low.index.date)
        temp1 = ((temp_high.max()-temp_low.min())/temp_low.min()).mean(axis = 1)
        #ts_rank window: 30
        a2 = ts_rank(temp1.to_frame(), 30)
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
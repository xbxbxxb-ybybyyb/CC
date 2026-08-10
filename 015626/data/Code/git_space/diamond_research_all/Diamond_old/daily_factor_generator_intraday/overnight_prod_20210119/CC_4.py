# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:26:07 2020

@author: appadmin
"""

from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd

class CC_4(FactorGenerator):
    def __init__(self):

        required_columns =['volume', 'recent_month_mask']
 
        super(CC_4, self).__init__(required_columns=required_columns)
    def on_bar(self, data):
        temp_volume = (data['volume'][data['recent_month_mask']]).between_time('09:30', '14:49')
        temp_volume = temp_volume.groupby(temp_volume.index.date)
        temp1 = temp_volume.std().mean(axis = 1) 
        #ts_rank window: 60
        a2 = ts_rank(temp1.to_frame(), 60)
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
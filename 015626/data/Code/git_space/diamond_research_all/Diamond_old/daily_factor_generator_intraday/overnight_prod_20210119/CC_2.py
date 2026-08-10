# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:22:45 2020

@author: appadmin
"""

from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd

class CC_2(FactorGenerator):
    def __init__(self):

        required_columns =['vwap', 'recent_month_mask']
 
        super(CC_2, self).__init__(required_columns=required_columns)
    def on_bar(self, data):
        temp = (data['vwap'][data['recent_month_mask']]).between_time('09:30', '14:49')
        temp = temp.groupby(temp.index.date)
        temp1 = ((temp.last()-temp.min())/temp.min()).mean(axis = 1)
        a2 = ts_rank(temp1.to_frame(), 90)
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
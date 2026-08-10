# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:32:13 2020

@author: appadmin
"""

from factor_generator import FactorGenerator
from operators_cc import *
import pandas as pd

class CC_6(FactorGenerator):
    def __init__(self):

        required_columns =['amount', 'close', 'volume', 'recent_month_mask']
 
        super().__init__(required_columns=required_columns)
    def on_bar(self, data):
        amount_total = (data['amount'][data['recent_month_mask']]).between_time('14:40', '14:49')
        amount_total = amount_total.groupby(amount_total.index.date).sum().sum(axis=1)
        temp11 = ((data['close']-data['close'].shift(1))/abs((data['close']-data['close'].shift(1)))*data['close']*(data['volume']))
        temp111 = temp11[data['recent_month_mask']].between_time('14:40', '14:49')
        temp111 = temp111.groupby(temp111.index.date).sum().sum(axis=1)
        temp1 = -temp111 / amount_total
        temp1.index = pd.to_datetime(temp1.index)
        a2 = ts_rank(temp1.to_frame(), 5)
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
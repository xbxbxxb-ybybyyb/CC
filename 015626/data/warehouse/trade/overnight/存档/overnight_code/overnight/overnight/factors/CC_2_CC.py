# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:11:33 2021

@author: appadmin
"""

from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_2_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):

        required_columns =['vwap_IC.CFE', 'recent_month_mask']
 
        super(CC_2_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=90, **kwargs)
    def on_bar(self, data):
        temp = (data['vwap_IC.CFE'][data['recent_month_mask']]).between_time(futures_data_morning_begin, trade_stop_time)
        temp = temp.groupby(temp.index.date)
        temp1 = ((temp.last()-temp.min())/replace_zero(temp.min())).mean(axis = 1)
        a2 = temp1.to_frame()
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
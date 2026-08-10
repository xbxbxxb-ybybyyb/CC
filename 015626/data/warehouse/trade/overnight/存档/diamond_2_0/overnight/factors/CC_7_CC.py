# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:10:22 2021

@author: appadmin
"""

from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_7_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):

        required_columns =['high_IC.CFE','low_IC.CFE','recent_month_mask']
 
        super(CC_7_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)
    def on_bar(self, data):
        minute = trade_stop_time.minute
        hour = trade_stop_time.hour

        if minute < 49:
            minute = 60 + minute - 49
            hour = hour - 1
        else:
            minute = minute - 49

        temp_high = (data['high_IC.CFE'][data['recent_month_mask']]).between_time(datetime.time(hour, minute), trade_stop_time)
        temp_high = temp_high.groupby(temp_high.index.date)
        temp_low = (data['low_IC.CFE'][data['recent_month_mask']]).between_time(datetime.time(hour, minute), trade_stop_time)
        temp_low = temp_low.groupby(temp_low.index.date)
        a2 = ((temp_high.max()-temp_low.min())/replace_zero(temp_low.min())).mean(axis = 1).to_frame()
        
        a2.index = pd.to_datetime(a2.index)
        a2.index.name = 'dt'
        a2.columns = [self.__class__.__name__]
        return a2
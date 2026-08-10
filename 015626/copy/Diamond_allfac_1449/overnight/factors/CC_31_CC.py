# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:11:55 2021

@author: appadmin
"""

import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *

class CC_31_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns=['close_IF.CFE', 'volume_IF.CFE', 'recent_month_mask']

        super(CC_31_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

        
    def on_bar(self, data):

        temp1 = data['close_IF.CFE'].diff()
        temp2 = np.abs(data['volume_IF.CFE'] * temp1)
        temp2 = temp2[data['recent_month_mask']].mean(axis = 1).to_frame()
        hdl_ind_r = temp2.rolling(30, min_periods = 10).mean()
        a1 = hdl_ind_r

        minute = trade_stop_time.minute
        hour = trade_stop_time.hour

        if minute < 4:
            minute = 60 + minute - 4
            hour = hour - 1
        else:
            minute = minute - 4

        temp = a1.between_time(datetime.time(hour, minute), trade_stop_time)
        temp = temp.groupby(temp.index.date).mean()
        temp.index.name = 'dt'
        temp.columns = [self.__class__.__name__]
        temp.index = pd.to_datetime(temp.index)
        return temp
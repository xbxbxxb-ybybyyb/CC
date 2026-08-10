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

class CC_32_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns=['close_000905.SH']

        super(CC_32_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

        
    def on_bar(self, data):
        columnname = self.__class__.__name__

        minute = futures_data_afternoon_end.minute
        hour = futures_data_afternoon_end.hour

        if minute < 1:
            minute = 60 + minute - 1
            hour = hour - 1
        else:
            minute = minute - 1

        temp = data['close_000905.SH'].between_time(futures_data_morning_begin, datetime.time(hour, minute))
        temp = temp.pct_change().between_time(futures_data_morning_begin, trade_stop_time)
        
        factor = temp.groupby(temp.index.date).skew().to_frame()
        factor.index.name = 'dt'
        #factor = (1-abs(ts_rank(-factor.to_frame(), 20)))*2-1
        factor = -factor
        factor.columns = [columnname]

        factor.columns = [self.__class__.__name__]
        factor.index = pd.to_datetime(factor.index)
        return factor
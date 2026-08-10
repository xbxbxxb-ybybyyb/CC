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

class CC_29_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns=['close_000300.SH', 'close_IF.CFE', 'recent_month_mask']

        super(CC_29_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

        
    def on_bar(self, data):
        close_spot = data['close_000300.SH']
        close = data['close_IF.CFE']
        vwtc_r = close.rolling(50, min_periods=15).corr(close_spot)
        vwtc_r  = vwtc_r.replace([-np.inf, np.inf], np.nan)
        vwtc_r = vwtc_r[data['recent_month_mask']]
        factor = (vwtc_r*(np.sign(-(close.sub(close_spot,axis=0))))[data['recent_month_mask']]).mean(axis = 1)
        factor = np.abs(factor)
        
        minute = trade_stop_time.minute
        hour = trade_stop_time.hour
        if minute < 19:
            minute = 60 + minute - 19
            hour = hour - 1
        else:
            minute = minute - 19

        temp1 = factor.between_time(datetime.time(hour, minute), trade_stop_time)
        temp1 = temp1.groupby(temp1.index.date).mean().to_frame()
        temp1.index.name = 'dt'

        temp1.columns = [self.__class__.__name__]
        temp1.index = pd.to_datetime(temp1.index)
        return temp1
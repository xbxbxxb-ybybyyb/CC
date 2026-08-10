# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:09:05 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
from overnight.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_13_if_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['close_000300.SH']

        super(CC_13_if_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=70, **kwargs)

    def on_bar(self, data):
        close = data['close_000300.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        temp = close.rolling(90, min_periods = 2).mean().diff()
        dd1 = temp.between_time(futures_data_afternoon_begin, trade_stop_time)
        dd1 = dd1.groupby(dd1.index.date).mean().to_frame()
 
        dd1.index = pd.to_datetime(dd1.index)
        dd1.index.name = 'dt'
        dd1.columns = [self.__class__.__name__]
        return dd1
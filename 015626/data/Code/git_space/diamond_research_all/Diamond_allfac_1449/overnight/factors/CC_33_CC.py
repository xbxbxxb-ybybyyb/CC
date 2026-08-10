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

class CC_33_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns=['close_000905.SH', 'volume_000905.SH']

        super(CC_33_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=20, **kwargs)

        
    def on_bar(self, data):
        minute = futures_data_afternoon_end.minute
        hour = futures_data_afternoon_end.hour

        if minute < 1:
            minute = 60 + minute - 1
            hour = hour - 1
        else:
            minute = minute - 1

        high = data['close_000905.SH'].between_time(futures_data_morning_begin, datetime.time(hour, minute))

        close = data['volume_000905.SH'].between_time(futures_data_morning_begin, datetime.time(hour, minute))
        
        s = high.rolling(90, min_periods=10).std()
        f = close.rolling(90, min_periods=10).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(90, min_periods=10).cov(close) / (s * f)

        t_pcor2[abs(t_pcor2) > 1e8] = 0
        dd1 = t_pcor2.between_time(futures_data_morning_begin, trade_stop_time)
        dd1 = dd1.groupby(dd1.index.date).mean().to_frame()
        dd1.index.name = 'dt'

        dd1.columns = [self.__class__.__name__]
        dd1.index = pd.to_datetime(dd1.index)
        return -dd1
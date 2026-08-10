# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:11:55 2021

@author: appadmin
"""
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_12_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns=['high_000905.SH', 'close_000905.SH']

        super(CC_12_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=30, **kwargs)

            
    def on_bar(self, data):
        high = data['high_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        close = data['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        t_pcor2 = high.rolling(60, min_periods=30).corr(close)
        
        t_pcor2[abs(t_pcor2) > 1] = np.nan
        dd1 = t_pcor2.between_time(futures_data_afternoon_begin, trade_stop_time)
        dd1 = dd1.groupby(dd1.index.date).mean().to_frame()
        
        dd1.index = pd.to_datetime(dd1.index)
        dd1.index.name = 'dt'
        dd1.columns = [self.__class__.__name__]
        return dd1
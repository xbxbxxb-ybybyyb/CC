# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:21:38 2021

@author: appadmin
"""


from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class GC001_6_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_204001.SH', 'open_204001.SH']
        super(GC001_6_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=25, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__
        open1 = df['open_204001.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        close = df['close_204001.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        a = close - open1
        a[a>0] = 1
        a[a<0] = -1

        t = (a).groupby(a.index.date).sum()
        t114 = t.to_frame()
        t114.index = pd.to_datetime(t114.index)
        t114.columns = [self.__class__.__name__]
        return t114
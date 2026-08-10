# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:25:56 2021

@author: appadmin
"""

from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class ICIF4_CC_IF(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super(ICIF4_CC_IF, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__
        close = df['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        temp = close.rolling(60, min_periods = 15).mean() - close.shift(20).rolling(40, min_periods = 7).mean()
        factor = temp.to_frame()
        
        factor = np.abs(factor)

        factor = ts_rank(factor, 1200)

        factor[factor<=-0.5] = 0
        
        t = factor.at_time(trade_stop_time)
        t.index = pd.to_datetime(t.index.date)
        t.index.name = 'dt'
        t.columns = [self.__class__.__name__]
        return t
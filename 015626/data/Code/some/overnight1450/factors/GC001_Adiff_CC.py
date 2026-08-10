# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:23:11 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class GC001_Adiff_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['amount_204001.SH']
        super(GC001_Adiff_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=25, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__

        t = df['amount_204001.SH'].between_time(futures_data_morning_begin, futures_data_morning_end)
        t2 = df['amount_204001.SH'].between_time(futures_data_afternoon_begin, trade_stop_time)
        t = t.groupby(t.index.date).mean() - t2.groupby(t2.index.date).mean()
 
        t128 = t.to_frame()
        t128.index = pd.to_datetime(t128.index)
        t128.columns = [self.__class__.__name__]
        return t128
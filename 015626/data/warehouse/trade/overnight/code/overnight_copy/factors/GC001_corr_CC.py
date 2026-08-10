# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 13:39:03 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd


class GC001_corr_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_204001.SH', 'close_IH.CFE', 'recent_month_mask']
        super(GC001_corr_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=15, **kwargs)

    def on_bar(self, df):
        #columnname = self.__class__.__name__
        GC_close =  df['close_204001.SH'].between_time(futures_data_morning_begin, trade_stop_time)
        close_ih = df['close_IH.CFE'][df['recent_month_mask']].mean(axis = 1).between_time(futures_data_morning_begin, trade_stop_time)
        t = (close_ih.rolling(150, min_periods = 60).corr(GC_close))
        t = -t.between_time(futures_data_afternoon_begin, trade_stop_time)
        t = t.groupby(t.index.date).mean().to_frame()
        t.index.name = 'dt'
        t.index = pd.to_datetime(t.index)
        t.columns = [self.__class__.__name__]
        return t
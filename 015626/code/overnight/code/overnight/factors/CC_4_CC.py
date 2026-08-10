# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 10:20:00 2021

@author: appadmin
"""

from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CC_4_CC(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['volume_IC.CFE', 'recent_month_mask']
        super(CC_4_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

    def on_bar(self, df):

        suffix = '_IC.CFE'
        cif = df['volume' + suffix].between_time(futures_data_morning_begin, trade_stop_time)
        temp_volume = (cif[df['recent_month_mask'].between_time(futures_data_morning_begin, trade_stop_time)])
        temp_volume = temp_volume.groupby(temp_volume.index.date)
        temp1 = temp_volume.std().dropna(how = 'all').mean(axis = 1).to_frame()
        #ts_rank window: 60
        #a2 = ts_rank(temp1.to_frame(), 60)
        temp1.index = pd.to_datetime(temp1.index)
        temp1.columns = [self.__class__.__name__]
        return temp1
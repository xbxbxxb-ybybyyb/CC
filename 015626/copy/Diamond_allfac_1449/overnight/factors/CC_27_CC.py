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

class CC_27_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        
        required_columns = ['close_IC.CFE','recent_month_mask']

        super(CC_27_CC, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=40, **kwargs)

        
    def on_bar(self, data):
        columnname = self.__class__.__name__
        temp = data['close_IC.CFE'][data['recent_month_mask']].mean(axis = 1)
        temp = temp.between_time(futures_data_morning_begin, trade_stop_time)
        temp = temp.groupby(temp.index.date)
        factor = (temp.max() - temp.min()).to_frame()

        factor.index.name = 'dt'

        factor.columns = [columnname]
        factor.index = pd.to_datetime(factor.index)
        return factor
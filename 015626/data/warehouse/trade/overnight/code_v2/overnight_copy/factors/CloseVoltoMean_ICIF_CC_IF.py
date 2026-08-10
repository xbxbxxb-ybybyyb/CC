# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 09:04:57 2021

@author: appadmin
"""
from overnight.utility import *
from overnight.factor_generator import FactorGenerator
from overnight.naming_config import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CloseVoltoMean_ICIF_CC_IF(FactorGenerator):

    def __init__(self, *args, **kwargs):
        required_columns=['close_000905.SH']
        super(CloseVoltoMean_ICIF_CC_IF, self).__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=0, **kwargs)

    def on_bar(self, data):
        close = data['close_000905.SH'].between_time(futures_data_morning_begin, futures_data_afternoon_end)
        
        prstd3_r = close.rolling(30, min_periods =10).std()/close.rolling(30, min_periods =15).mean()
        prstd3_r[abs(prstd3_r)>100000] = np.nan
        prstd3_r = prstd3_r.rolling(15, min_periods = 2).mean()
        factor = prstd3_r.to_frame()

        factor.columns =  [self.__class__.__name__]
        factor = ts_rank(factor, 1200)
        factor[factor>1] = 0
        factor[factor<=-0.5] = 0
        factor = factor.iloc[factor.index.indexer_at_time(trade_stop_time)]
        factor.index = pd.to_datetime(factor.index.date)
        factor.index.name = 'dt'
        return factor
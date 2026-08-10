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

class CC_11_CC(FactorGenerator):
    def __init__(self, *args, **kwargs):
        name1 = 'close_alla_preadj'
        name2 = 'amount_alla' 
        name3 = 'high_alla_preadj' 
        name4 = 'low_alla_preadj' 
        name5 = 'open_alla_preadj'
        required_columns=[name1, name2, name3, name4, name5]

        super().__init__(*args, required_columns=required_columns, ts_norm_method='ts_rank', ts_norm_bars=60, **kwargs)

        
    def on_bar(self, data_dict):
        #import pdb; pdb.set_trace()
        zz800_stk_list = self.get_mdconstant('zz500_stock_list')
        amount = data_dict['amount_alla'][zz800_stk_list]
        high = data_dict['high_alla_preadj'][zz800_stk_list]
        low = data_dict['low_alla_preadj' ][zz800_stk_list]
        close = data_dict['close_alla_preadj'][zz800_stk_list]
        hopen = data_dict['open_alla_preadj'][zz800_stk_list]       
        df_s = amount.rolling(120, min_periods = 15).sum()
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        
        a = high.rolling(120, min_periods = 60).max()-hopen.shift(120)
        b = close - low.rolling(120, min_periods = 60).min()
        c = (high.rolling(120, min_periods = 60).max()-low.rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/replace_zero(c)
        factor = (vwtc_r[bool_df]).mean(axis = 1)
        dd1 = factor.between_time(futures_data_morning_begin, trade_stop_time)
        dd1 = dd1.groupby(dd1.index.date).mean().to_frame()
        dd1 = -dd1
        dd1.index = pd.to_datetime(dd1.index)
        dd1.index.name = 'dt'
        dd1.columns = [self.__class__.__name__]
        return dd1
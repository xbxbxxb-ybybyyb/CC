
# coding: utf-8

# In[ ]:
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import ts_pct_change
from future_factor import FutureFactor

class LYM_CFG_7_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close']
    normalize_size = 600
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):
        
        c = df['close'][-11:]
        factor = (c.rolling(10).max() - c.shift(10))*(c - c.shift(10))
        factor = factor.mean(axis = 1)[-1]

        return factor


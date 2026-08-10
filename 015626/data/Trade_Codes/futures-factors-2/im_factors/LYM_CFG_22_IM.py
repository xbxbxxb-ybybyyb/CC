
# coding: utf-8

# In[ ]:
import numpy as np
import numpy.ma as ma
import bottleneck as bk
from operators_cc import *
from operators_wsc_1_0 import *
from future_factor import FutureFactor

class LYM_CFG_22_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','amount','volume','weight','adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = True


    def calculate(self, df):
        
        a = df['close_preadj'][-5:]
        b = df['volume_preadj'][-5:]

        w = df['weight'][-5:]

        factor = (((2 * (a > a.shift(1))) - 1).rolling(3).sum() * b.rolling(5).sum()).sum(axis = 1)[-1]

        
        return factor



# coding: utf-8

# In[ ]:


import numpy as np
from future_factor import FutureFactor
import pandas as pd
import bottleneck as bk
from operators_cc import *

class LYM_CFG_27(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = True


    def calculate(self, df):
        
        a = df['close_preadj'][-102:]

        w = df['weight'][-102:]

        b = a - a.rolling(100).min()
        c = a.diff(3)

        b[(a.pct_change(100).abs() - 0.02) > 1e-9] = c

        factor = b

        factor = (factor * w[w.gt(w.quantile(0.8, axis = 1), axis = 0)]).sum(axis = 1)[-1]

        
        return factor


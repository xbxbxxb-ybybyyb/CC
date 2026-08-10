
# coding: utf-8

# In[ ]:

import numpy as np
from future_factor import FutureFactor
import pandas as pd
import bottleneck as bk
from operators_cc import *


class LYM_CFG_12_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['AbsPxPath', 'close', 'weight']
    normalize_size = 240
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None


    def calculate(self, df):

        a = df['AbsPxPath'][-5:]
        b = df['close'][-5:]
        w = df['weight'][-5:]

        factor = (w * a[a.gt(a.quantile(0.8, axis = 1), axis = 0)] * b.diff() / b).mean(axis = 1)

        factor = factor.rolling(4).mean()[-1]

        return factor


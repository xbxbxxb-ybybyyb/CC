# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 13:54:13 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator
import numpy as np
from joblib import Parallel, delayed
from operators_cc import *

class Amount_D2_CC(FactorGenerator):
    def __init__(self):
        required_columns=['recent_month_mask', 'amount']

        super(Amount_D2_CC, self).__init__(required_columns=required_columns
                                  )
   
    

    def on_bar(self, data):
        #2974.6403__2974.6403__2974.6403__ts_max(decay_linear(ts_median(high, 20), 30), 40)
        amount = data['amount'][data['recent_month_mask']].mean(axis =1)
        temp = amount.rolling(40, min_periods = 20).max()
        temp1 = np.array([temp])
        prstd_r = pd.Series(decay_linear(decay_linear(temp1, 35), 5)[0])
        prstd_r.index = amount.index
        factor = prstd_r
        factor = ts_rank(factor.to_frame(), 242)
        factor.columns = [self.__class__.__name__]
        return factor
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 16:48:06 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

# demo

# demo

def normalization(signal, holding_window = 1200): 
    max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
    min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
    a = (signal - min_s)/(max_s-min_s)
    a = 2*a-1
    aa = pd.DataFrame(a)
    aa.index = signal.index
    aa.columns = signal.columns
    return aa

class CLP_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'position', 'recent_month_mask']

        super(CLP_CC, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):

        temp1 = (pd.DataFrame(np.where(data['close']>0, 1, np.where(data['close']<0, -1, 0))))
        temp1.index = data['close'].index
        temp1.columns = data['close'].columns
        temp1 = (temp1[data['recent_month_mask']]).mean(axis = 1)
        temp3 = ((data['position'].diff())[data['recent_month_mask']]).mean(axis = 1)
        temp3.index = data['position'].index
        temp2 = np.abs(temp3 * (temp1))
        hdl_ind_r = temp2.rolling(30, min_periods = 15).mean()
        factor = hdl_ind_r.to_frame()
        factor.columns = [self.__class__.__name__]
        
        factor = normalization(factor)
        factor[factor<-0.3]=0
        return factor

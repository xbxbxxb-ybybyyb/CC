# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:50:34 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class LSC_CC_ind(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot', 'low_spot', 'close_spot']

        super(LSC_CC_ind, self).__init__(
                                  required_columns=required_columns)

    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        a = data['high_spot'].rolling(30, min_periods = 10).max() - data['low_spot'].rolling(30, min_periods = 10).min()
        a[abs(a)<1e-8] = np.nan
        b = data['high_spot'].rolling(30, min_periods = 10).max() - data['low_spot'].rolling(30, min_periods = 10).min()
        b[abs(b) < 1e-8] = np.nan
        hh = (data['high_spot'].rolling(30, min_periods = 10).max() - data['close_spot']) / a
        ll = (data['close_spot'] - data['low_spot'].rolling(30, min_periods = 10).min()) / b
        vwtc_r = ll.rolling(40, min_periods = 20).mean()-hh.rolling(40, min_periods = 20).mean()
        factor = vwtc_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<-0.8] = np.nan
        return factor
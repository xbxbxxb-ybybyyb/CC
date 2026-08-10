# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 14:28:37 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class HDLD_ind_CC(FactorGenerator):
    def __init__(self):
        required_columns =['open_spot', 'close_spot']
        super(HDLD_ind_CC, self).__init__(
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
        temp1 = pd.Series(np.where(data['open_spot']>data['close_spot'], data['open_spot'], data['close_spot']))
        temp2 = pd.Series(np.where(data['open_spot']>data['close_spot'], data['close_spot'], data['open_spot']))
        t_pcorr = (temp1.diff()+temp2.diff()).rolling(60, min_periods = 15).mean()
        factor = t_pcorr.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<0]=np.nan
        return factor

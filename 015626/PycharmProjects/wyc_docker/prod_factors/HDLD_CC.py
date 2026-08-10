# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 14:34:14 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

# demo
class HDLD_CC(FactorGenerator):
    def __init__(self):
        required_columns =['open', 'close']
        super(HDLD_CC, self).__init__(
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
        temp1 = pd.Series(np.where(data['open']>data['close'], data['open'], data['close']))
        temp2 = pd.Series(np.where(data['open']>data['close'], data['close'], data['open']))
        t_pcorr = (temp1.diff()+temp2.diff()).rolling(90, min_periods = 45).mean()
        factor = t_pcorr.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<0]=np.nan
        return factor

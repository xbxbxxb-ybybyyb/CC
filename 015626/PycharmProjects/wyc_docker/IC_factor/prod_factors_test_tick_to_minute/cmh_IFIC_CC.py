# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 19:05:19 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

# 多头因子

def normalization(signal, holding_window = 1200): 
    max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
    min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
    a = (signal - min_s)/(max_s-min_s)
    a = 2*a-1
    aa = pd.DataFrame(a)
    aa.index = signal.index
    aa.columns = signal.columns
    return aa

class cmh_IFIC_CC(FactorGenerator):
    def __init__(self):
        required_columns =['high_if', 'close_if']
        
        super(cmh_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        vwtc_r = (data['high_if']-data['close_if'].rolling(90, min_periods = 30).mean())
        factor = vwtc_r.to_frame()
        factor.index = data.index

        factor.columns = [self.__class__.__name__]
        factor = np.abs(factor)
        factor = normalization(factor)
        factor[factor<=-0.5] = np.nan
        factor[factor>1] = np.nan
        return factor


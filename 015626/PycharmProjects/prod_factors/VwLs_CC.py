# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:59:33 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

def normalization(signal, holding_window = 1200): 
    max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
    min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
    a = (signal - min_s)/(max_s-min_s)
    a = 2*a-1
    aa = pd.DataFrame(a)
    aa.index = signal.index
    aa.columns = signal.columns
    return aa

class VwLs_CC(FactorGenerator):
    def __init__(self):

        required_columns =['vwap']

        super(VwLs_CC, self).__init__(
                                  required_columns=required_columns
                                  )
    
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        price_diff_1 = data['vwap']/data['vwap'].shift(1)-1
        price_diff_30 = data['vwap']/data['vwap'].shift(60)-1
        copcor1_r = -(price_diff_1-price_diff_30).rolling(15, min_periods = 5).mean()       
        factor = copcor1_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = normalization(factor, 720)
        factor[factor<=-0.5] = np.nan
        return factor

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:27:15 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator

class LSC_ind_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot_if', 'low_spot_if', 'close_spot_if']

        super(LSC_ind_IFIC_CC, self).__init__(
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
        a = (data['high_spot_if'].rolling(30, min_periods = 10).max() - data['low_spot_if'].rolling(30, min_periods = 10).min())
        a[abs(a)<1e-8] = np.nan
        b = (data['high_spot_if'].rolling(30, min_periods = 10).max() - data['low_spot_if'].rolling(30, min_periods = 10).min())
        b[abs(b)<1e-8] = np.nan
        hh = (data['high_spot_if'].rolling(30, min_periods = 10).max() - data['close_spot_if'])/ a 
        ll = (data['close_spot_if'] - data['low_spot_if'].rolling(30, min_periods = 10).min())/ b 
        vwtc_r = ll.rolling(45, min_periods = 10).mean()-hh.rolling(45, min_periods = 10).mean()
        factor = vwtc_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<=-0.5] = np.nan
        return factor
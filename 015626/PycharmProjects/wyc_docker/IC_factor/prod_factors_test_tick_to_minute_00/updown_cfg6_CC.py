# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 15:32:10 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class updown_cfg6_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns =['close_zz500', 'position']
        super(updown_cfg6_CC, self).__init__(
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
        hc = data['close_zz500']/data['close_zz500'].shift(1)-1
        upclose = (hc>0).sum(axis = 1)
        downclose = (hc<0).sum(axis = 1)
        temp = np.where((data['position']>data['position'].shift(1)) & (upclose>downclose), 4, np.where((data['position']<data['position'].shift(1)) & (upclose<downclose), 0, 1))
        temp = pd.Series(temp)
        temp.index = hc.index
        vwtc_r = temp.rolling(120, min_periods = 15).mean()
        factor = vwtc_r.to_frame()


        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor>1] = np.nan
        factor[factor<=-0.5] = np.nan
        return factor
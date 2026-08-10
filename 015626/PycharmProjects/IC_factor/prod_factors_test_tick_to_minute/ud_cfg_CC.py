# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 09:51:44 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

# 多头因子

class ud_cfg_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500']
        lookback_bars=2000
        super(ud_cfg_CC, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)
    

    
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
        t_prcd2= (upclose-downclose).rolling(60, min_periods = 15).mean()
        factor = t_prcd2.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<=-0.5] = np.nan
        factor[factor>1] = np.nan

        return factor
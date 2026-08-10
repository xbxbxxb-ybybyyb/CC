# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 09:51:44 2020

@author: appadmin
"""
import pandas as pd
from factor_generator import FactorGenerator
import numpy as np

# 多头因子
class ud_cfg_CC(FactorGenerator):
    def __init__(self):
        required_columns =['upclose', 'downclose']
        
        super(ud_cfg_CC, self).__init__(
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
        t_prcd2= (data['upclose']-data['downclose']).rolling(60, min_periods = 15).mean()
        factor = t_prcd2.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor)
        factor[factor<-0.3] = np.nan
        factor[factor>1] = np.nan

        return factor
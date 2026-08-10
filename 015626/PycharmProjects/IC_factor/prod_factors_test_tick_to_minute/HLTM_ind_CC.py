# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 16:38:25 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

def ts_rank(test, n=1200):
    a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
    aa = pd.DataFrame(a)
    aa.index = test.index
    aa.columns = test.columns
    return aa

class HLTM_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'high_spot', 'low_spot']

        super(HLTM_ind_CC, self).__init__(
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
        temp1 = data['high_spot'].rolling(15, min_periods = 7).max()-data['close_spot']
        temp2 = data['close_spot']-data['low_spot'].rolling(15, min_periods = 7).min()
        temp = pd.Series(np.where(temp1>temp2, temp1, temp2))
        temp.index = temp1.index
        vwtc_r = (temp).rolling(30, min_periods = 15).mean()
        
        factor = vwtc_r.to_frame()
        factor.index = data.index

        factor.columns = [self.__class__.__name__]
        factor = self.normalization(factor, 242*4)
        factor = ts_rank(factor)
        factor[factor<-1] = np.nan
        factor[factor>1] = np.nan
        return factor
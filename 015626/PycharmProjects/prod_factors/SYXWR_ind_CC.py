# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:28:04 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class SYXWR_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'low_spot', 'open_spot', 'high_spot']

        super(SYXWR_ind_CC, self).__init__(
                                  required_columns=required_columns)

    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        temp1 = pd.Series(np.where(data['open_spot']>data['close_spot'], data['open_spot'], data['close_spot']))
        temp2 = pd.Series(np.where(data['open_spot']>data['close_spot'], data['close_spot'], data['open_spot']))
        temp1.index = data.index
        temp2.index = data.index
        t_pcor = (data['high_spot']-temp1)/(data['high_spot'] - temp1).rolling(30, min_periods = 15).mean()
        t_pcor2 = (data['close_spot']-data['low_spot'].rolling(30, min_periods = 15).min())/(data['high_spot'].rolling(30, min_periods = 15).max()-data['low_spot'].rolling(30, min_periods = 15).min())
        t_pcorr = (t_pcor2 - t_pcor).rolling(90, min_periods = 20).mean()
        factor = t_pcorr.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor


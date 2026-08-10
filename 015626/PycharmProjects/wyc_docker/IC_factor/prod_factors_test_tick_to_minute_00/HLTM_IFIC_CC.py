# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 16:17:24 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class HLTM_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['vwap_if', 'high_if', 'low_if']

        super(HLTM_IFIC_CC, self).__init__(
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
        temp1 = data['high_if'].rolling(15, min_periods = 7).max()-data['vwap_if']
        temp2 = data['vwap_if']-data['low_if'].rolling(15, min_periods = 7).min()
        temp = pd.Series(np.where(temp1>temp2, temp1, temp2))
        temp.index = temp1.index
        vwtc_r = temp.rolling(40, min_periods = 15).mean()
        
        factor = vwtc_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<-1] = np.nan
        factor[factor>1] = np.nan
        return factor

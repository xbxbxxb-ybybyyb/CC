# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:11:11 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class HmaxC_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'high_spot']

        super(HmaxC_ind_CC, self).__init__(
                                  required_columns=required_columns)
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        hmhm_r = -data['high_spot'].rolling(120, min_periods = 90).max()/data['close_spot']
        factor = hmhm_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<-0.5]=np.nan
        return factor
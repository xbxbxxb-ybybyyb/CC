# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 10:50:31 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class HLLSVol_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low']
 
        super(HLLSVol_CC, self).__init__(
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
        a = (data['high']/data['low']).rolling(240, min_periods =10).std()
        a[a<1e-10] = np.nan
        ocre3_r = (data['high']/data['low']).rolling(40, min_periods =10).std()/a
        factor = ocre3_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<0]=np.nan
        return factor

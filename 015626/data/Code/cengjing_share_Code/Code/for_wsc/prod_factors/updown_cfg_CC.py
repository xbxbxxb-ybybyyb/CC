# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 18:21:58 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
       
# ts_rank(1200)
class updown_cfg_CC(FactorGenerator):
    def __init__(self):
   
        required_columns =['upclose', 'downclose']
        super(updown_cfg_CC, self).__init__(
                                  required_columns=required_columns)
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):
        vwtc_r = (data['upclose']-data['downclose']).rolling(40, min_periods = 10).mean().ewm(span=3,adjust=False,min_periods=2).mean()
        factor = vwtc_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor<-0.5]=np.nan
        return factor
    
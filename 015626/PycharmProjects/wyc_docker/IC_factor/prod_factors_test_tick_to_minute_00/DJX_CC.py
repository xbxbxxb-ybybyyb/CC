# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 09:03:18 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator import FactorGenerator

class DJX_CC(FactorGenerator):
    def __init__(self):
        required_columns =['close']

        super(DJX_CC, self).__init__(
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
        temp5 = data['close'].rolling(5, min_periods = 2).mean()
        temp10 = data['close'].rolling(10, min_periods = 5).mean()
        temp20 = data['close'].rolling(20, min_periods = 10).mean()
        temp60 = data['close'].rolling(60, min_periods = 30).mean()
        temp120 = data['close'].rolling(120, min_periods = 60).mean()
        temp5_diff = (temp5.diff()>0).astype(int)
        temp10_diff = (temp10.diff()>0).astype(int)
        temp20_diff = (temp20.diff()>0).astype(int)
        temp60_diff = (temp60.diff()>0).astype(int)
        temp120_diff = (temp120.diff()>0).astype(int)
        temp = (temp5_diff+temp10_diff+temp20_diff+temp60_diff+temp120_diff).rolling(20, min_periods = 15).mean()
        factor = self.ts_rank(temp.to_frame())
        factor.iloc[:, 0] = factor.iloc[:, 0].rolling(10, min_periods = 2).mean()

        #factor = self.ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor
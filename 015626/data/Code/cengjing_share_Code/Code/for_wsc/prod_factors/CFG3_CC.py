# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 17:01:46 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG3_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'weight_zz500', 'volume_zz500']
        lookback_bars=2000
        super(CFG3_CC, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, df):
        columnname = self.__class__.__name__       
        hclose = df['close_zz500']
        weight = df['weight_zz500']
        volume = df['volume_zz500']
        hret = (hclose/hclose.shift(1)-1)
        
        temp_v_weighted = weight*volume*hret
        vw = temp_v_weighted.sum(axis = 1)
        c = vw.copy()
        c = c.to_frame()
        c.index.name = 'dt'
        c1 = c.rolling(90, min_periods = 15).mean()
        c2 = self.ts_rank(c1)
        c2.columns = [columnname]
        return c2
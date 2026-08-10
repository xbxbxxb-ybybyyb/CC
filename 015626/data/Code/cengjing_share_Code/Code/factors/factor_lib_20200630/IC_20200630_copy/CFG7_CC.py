# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 13:49:19 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex

class CFG7_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_zz500', 'close_zz500', 'open_zz500', 'weight_boolean_zz500']

        super(CFG7_CC, self).__init__(required_columns=required_columns
                                  )
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def to_ts(self, df, ret, LS = True, Lag = False):
        if LS == True:
            if Lag == False:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
            else:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)-(df.lt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)
        else:
            if Lag == False:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret).mean(axis = 1)
            else:
                return (df.gt(pd.Series(df.median(axis = 1)), axis=0)*ret.shift(1)).mean(axis = 1)

    def on_bar(self, df):
        columnname = self.__class__.__name__
        to = df['turnover_zz500']
        hclose = df['close_zz500']
        
        hopen = df['open_zz500']
        ret = hclose/hopen -1
        hret = hclose/hclose.shift(1) -1
        cc1 = ((to[hclose<hopen]/abs(ret[hclose<hopen])))
        ccc1 = cc1.rolling(60, min_periods = 7).mean()
        ccc1 = ccc1[df['weight_boolean_zz500']]
        hret = hret[df['weight_boolean_zz500']]
        cc2 = self.to_ts(ccc1, hret)
        ccc2 = cc2.rolling(60, min_periods = 15).mean()
        cc3 = self.ts_rank(ccc2.to_frame())
        #cc3 = cc3.rolling(3, min_periods = 2).mean()
        cc3[cc3<=-1] = np.nan
        cc3[cc3>1] = np.nan
        cc3.columns = [columnname]
        return cc3

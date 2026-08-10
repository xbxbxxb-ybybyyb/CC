# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 13:53:15 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

def to_ts(df, ret, LS = True, Lag = False):
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

class CFG8_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['volume_zz500', 'close_zz500', 'float_shares_zz500', 'weight_boolean_zz500']

        super(CFG8_CC, self).__init__(required_columns=required_columns
                                  )
    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        hvolume = df['volume_zz500']
        hclose = df['close_zz500']
        hfs = df['float_shares_zz500']
        hret = hclose/hclose.shift(1) - 1
        d1 = hvolume/hclose/hfs
        d1 = d1[df['weight_boolean_zz500']]
        hret = hret[df['weight_boolean_zz500']]
        d1 = to_ts(d1, hret)
        dd1 = d1.rolling(30, min_periods = 15).mean()
        dd2 = rolling_norm(dd1.to_frame())
        dd2.columns = [columnname]
        dd2[dd2<=-0.5] = 0
        dd2[dd2>1] = np.nan
        
        return dd2
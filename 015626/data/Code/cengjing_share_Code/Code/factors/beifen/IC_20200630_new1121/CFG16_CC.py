# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 10:02:33 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
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


class CFG16_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'close_zz500', 'weight_boolean_zz500']
        lookback_bars=2000
        super(CFG16_CC, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)


    def on_bar(self, df):
        columnname = self.__class__.__name__

        hlow = df['low_zz500']
        hclose = df['close_zz500']
        hret = hclose/hclose.shift(1)-1
        i1 = -hlow.rolling(60, min_periods =15).min()/hlow.rolling(30, min_periods =10).mean()
        hret = hret[df['weight_boolean_zz500']]
        i1 = i1[df['weight_boolean_zz500']]
        i2 = to_ts(i1, hret)
        i2 = rolling_norm(i2.rolling(30, min_periods = 15).mean().to_frame(), method = 'ts_rank')
        i2 = i2.rolling(5, min_periods = 2).mean() 
        i2 = rolling_norm(i2, method = 'ts_rank')
        i2[i2>1] = np.nan
        i2[i2<=-0.5] = 0
        i2.columns = [columnname]    
        return i2
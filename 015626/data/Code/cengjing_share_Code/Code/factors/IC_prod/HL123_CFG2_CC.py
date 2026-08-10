# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:08:06 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class HL123_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'high_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(HL123_CFG2_CC, self).__init__(required_columns=required_columns)
    

    def normalization(self, signal, holding_window = 1200, ep_range = 3): 
        # Get rid of extreme values using 
        signal_mean = signal.rolling(holding_window,min_periods=int(holding_window/2)).mean() 
        signal_std = signal.rolling(holding_window,min_periods=int(holding_window/2)).std() 
        upper_bound = signal_mean + ep_range*signal_std
        lower_bound = signal_mean - ep_range*signal_std
        signal[signal>upper_bound] = upper_bound
        signal[signal<lower_bound] = lower_bound
        # Rolling Normalize
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        # In Case the input signal is not a DataFrame
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        # In case max_s = min_s
        signal[signal>1] = np.nan
        signal[signal<-1] = np.nan
        return aa

    def on_bar(self, df):
        columnname = self.__class__.__name__
        hlow = df['low_zz500']
        hhigh = df['high_zz500']
        df_s = df['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[df['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        i11 = hhigh.rolling(10, min_periods = 5).max()-hlow.rolling(60, min_periods = 10).min()
        i12 = (hhigh.shift(30)).rolling(10, min_periods = 5).max()-(hlow.shift(30)).rolling(60, min_periods = 10).min()
        i2 = (i11-i12).rolling(15, min_periods = 2).mean()
        i2 = ts_rank((i2[bool_df]).mean(axis = 1).to_frame())
        #i2 = rolling_norm(i2)
        #i2[i2>1] = np.nan
        i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2
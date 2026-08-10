# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 17:37:12 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class LSC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['high', 'low', 'close', 'recent_month_mask']

        super(LSC_CC, self).__init__(
                                  required_columns=required_columns)

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
    
    
    def on_bar(self, data):

        hh = (data['high'].rolling(30, min_periods = 10).max() - data['close'])/(data['high'].rolling(30, min_periods = 10).max() - data['low'].rolling(30, min_periods = 10).min()) 
        ll = (data['close'] - data['low'].rolling(30, min_periods = 10).min())/(data['high'].rolling(30, min_periods = 10).max() - data['low'].rolling(30, min_periods = 10).min())
        vwtc_r = ll.rolling(20, min_periods = 15).mean()-hh.rolling(20, min_periods = 15).mean()
        factor = vwtc_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        hh[abs(hh)>10000] = np.nan
        ll[abs(ll)>10000] = np.nan
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*4)
        factor[factor<=-0.5] = np.nan
        factor = factor.rolling(3, min_periods = 2).mean()
        factor = ts_rank(factor)
        # factor[factor<0] = 0
        return factor



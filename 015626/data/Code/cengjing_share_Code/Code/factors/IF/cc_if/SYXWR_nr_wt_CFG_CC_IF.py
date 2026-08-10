# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:40:40 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class SYXWR_nr_wt_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_hs300', 'weight_boolean_hs300', 'weight_hs300', 'low_hs300', 'high_hs300', 'turnover_hs300','open_hs300', 'close_hs300']
        super(SYXWR_nr_wt_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        temp4 = turnover.gt(pd.Series(turnover.quantile(0.80, axis = 1)), axis=0)
        stk_weight = (data['weight_hs300'])[data['weight_boolean_hs300']]        
        mask = stk_weight*temp4
        temp1 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['open_hs300'], data['close_hs300']))
        temp2 = pd.DataFrame(np.where(data['open_hs300']>data['close_hs300'], data['close_hs300'], data['open_hs300']))
        temp1.index = data['open_hs300'].index
        temp2.index = data['open_hs300'].index
        temp1.columns = data['open_hs300'].columns
        temp2.columns = data['open_hs300'].columns
        b = (data['high_hs300'] - temp1).rolling(30, min_periods = 15).mean()
        b[abs(b)<1e-8] = np.nan
        t_pcor = (data['high_hs300']-temp1)/b
        a = (data['high_hs300'].rolling(30, min_periods = 15).max()-data['low_hs300'].rolling(30, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (data['close_hs300']-data['low_hs300'].rolling(30, min_periods = 15).min())/a
        t_pcorr = (t_pcor2 - t_pcor)
        tempdf = (t_pcorr*mask).sum(axis = 1).to_frame()
        
        factor = rolling_norm(tempdf, 242*5)
        factor[abs(factor)>1] = np.nan
        
        factor = tempdf.rolling(45, min_periods = 10).mean()
        factor = ts_rank(factor) 
        factor.columns = [self.__class__.__name__]
        return factor
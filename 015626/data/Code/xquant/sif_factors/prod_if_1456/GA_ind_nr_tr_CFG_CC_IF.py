# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 18:19:29 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator_complex import FactorGeneratorComplex
import numpy as np

class GA_ind_nr_tr_CFG_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['high_hs300','open_hs300', 'low_hs300', 'weight_boolean_hs300', 'close_hs300', 'turnover_hs300']

        super(GA_ind_nr_tr_CFG_CC_IF, self).__init__(required_columns=required_columns
                                  )
    

    

    

    
    def on_bar(self, data):
        turnover = (data['turnover_hs300'].rolling(60, min_periods = 15).mean())[data['weight_boolean_hs300']]
        turnover_rank = 2 * turnover.rank(axis=1, pct=True) - 1
        mask = turnover_rank
        a = data['high_hs300'].rolling(120, min_periods = 60).max()-data['open_hs300'].shift(120)
        b = data['close_hs300'] - data['low_hs300'].rolling(120, min_periods = 60).min()
        c = (data['high_hs300'].rolling(120, min_periods = 60).max()-data['low_hs300'].rolling(120, min_periods = 60).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a+b)/c
        vwtc_r = rolling_norm(vwtc_r)
        tempdf = (vwtc_r*mask)
        tempdf = tempdf.sum(axis = 1).to_frame()
        factor = tempdf.rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
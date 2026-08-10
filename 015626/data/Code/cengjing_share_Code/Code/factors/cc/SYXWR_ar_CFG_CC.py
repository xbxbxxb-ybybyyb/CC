# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 09:28:50 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class SYXWR_ar_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'weight_boolean_zz500', 'close_zz500', 'open_zz500', 'high_zz500', 'low_zz500']
        super(SYXWR_ar_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, data):

        stk_amount = (data['amount_zz500'])[data['weight_boolean_zz500']]
        stk_amount_rank = 2 * stk_amount.rank(axis=1, pct=True) - 1
        
        temp1 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['open_zz500'], data['close_zz500']))
        temp2 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['close_zz500'], data['open_zz500']))
        temp1.index = data['open_zz500'].index
        temp2.index = data['open_zz500'].index
        temp1.columns = data['open_zz500'].columns
        temp2.columns = data['open_zz500'].columns
        b = (data['high_zz500'] - temp1).rolling(30, min_periods = 15).mean()
        b[abs(b)<1e-8] = np.nan
        t_pcor = (data['high_zz500']-temp1)/b
        a = (data['high_zz500'].rolling(30, min_periods = 15).max()-data['low_zz500'].rolling(30, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (data['close_zz500']-data['low_zz500'].rolling(30, min_periods = 15).min())/a
        t_pcorr = (t_pcor2 - t_pcor)
        factor = (t_pcorr*stk_amount_rank).sum(axis = 1).to_frame()
        factor = factor.rolling(40, min_periods = 20).mean()
        factor = ts_rank(factor, 2400)
        factor.columns = [self.__class__.__name__]
        return factor

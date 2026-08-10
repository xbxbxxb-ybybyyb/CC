# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 10:38:48 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *

class VLSM_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'weight_zz500', 'open_zz500', 'high_zz500', 'low_zz500', 'weight_boolean_zz500']
        
        super(VLSM_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    

    def on_bar(self, data):
        df_s = data['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[data['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        temp1 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['open_zz500'], data['close_zz500']))
        temp2 = pd.DataFrame(np.where(data['open_zz500']>data['close_zz500'], data['close_zz500'], data['open_zz500']))
        temp1.index = data['open_zz500'].index
        temp2.index = data['open_zz500'].index
        temp1.columns = data['open_zz500'].columns
        temp2.columns = data['open_zz500'].columns
        b = (data['high_zz500'] - temp1).rolling(40, min_periods = 15).mean()
        b[abs(b)<1e-8] = np.nan
        t_pcor = (data['high_zz500']-temp1)/b
        a = (data['high_zz500'].rolling(40, min_periods = 15).max()-data['low_zz500'].rolling(40, min_periods = 15).min())
        a[abs(a) < 1e-8] = np.nan
        t_pcor2 = (data['close_zz500']-data['low_zz500'].rolling(40, min_periods = 15).min())/a
        t_pcorr = (t_pcor2 - t_pcor).rolling(40, min_periods = 20).mean()
        factor = (t_pcorr[bool_df]).mean(axis = 1).to_frame()
        #factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        factor[factor<=-0.5] = np.nan
        return factor

# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:32:32 2020

@author: appadmin
"""
import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class HDLD_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'amount_zz500',  'open_zz500', 'weight_boolean_zz500']

        super(HDLD_CFG_CC, self).__init__(required_columns=required_columns
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
        t_pcorr = ((temp1 - temp1.shift(1))+(temp2 - temp2.shift(1))).rolling(60, min_periods = 45).mean()
        
        factor = (t_pcorr[bool_df]).mean(axis = 1)
        #factor.iloc[:, 0] = factor.iloc[:, 0].rolling(5, min_periods = 2).mean()
        factor = ts_rank(factor.to_frame())
        #factor = ts_rank(factor)
        #factor[factor<-0.5] = np.nan
        factor.columns = [self.__class__.__name__]
        return factor
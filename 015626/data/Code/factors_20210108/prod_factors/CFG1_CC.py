# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 10:22:33 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class CFG1_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_zz500', 'close_zz500', 'weight_zz500', 'weight_boolean_zz500']

        super(CFG1_CC, self).__init__(required_columns=required_columns
                                  )

    
    def on_bar(self, df):
        columnname = self.__class__.__name__
        df_s = df['amount_zz500'].rolling(120, min_periods = 15).sum()
        df_s = df_s[df['weight_boolean_zz500']]
        bool_df = df_s.gt(pd.Series(df_s.quantile(0.90, axis = 1)), axis=0)
        hclose = df['close_zz500']
        weight = df['weight_zz500']
        hret = (hclose/hclose.shift(1)-1)
        temp_weighted = hret*weight*bool_df
        a = (temp_weighted[df['weight_boolean_zz500']].mean(axis = 1))
        a = a.to_frame()
        a.index.name = 'dt'
        a1 = a.rolling(35, min_periods = 15).mean()
        a2 = rolling_norm(a1, method = 'ts_rank')
        #a2.iloc[:, 0] = a2.iloc[:, 0].rolling(3, min_periods = 2).mean()
        a2.columns = [columnname]
        #a2[a2<=-0.5] = np.nan
        #a2 = ts_rank(a2)
        return a2

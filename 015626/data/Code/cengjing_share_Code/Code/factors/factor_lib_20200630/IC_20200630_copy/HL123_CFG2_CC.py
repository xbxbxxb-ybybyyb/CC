# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 15:57:46 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex


class HL123_CFG2_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['low_zz500', 'high_zz500', 'amount_zz500', 'weight_boolean_zz500']

        super(HL123_CFG2_CC, self).__init__(required_columns=required_columns)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
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
        i2 = self.ts_rank((i2[bool_df]).mean(axis = 1).to_frame())
        #i2 = self.normalization(i2)
        #i2[i2>1] = np.nan
        i2[i2<=-0.5] = np.nan
        i2.columns = [columnname]    
        return i2
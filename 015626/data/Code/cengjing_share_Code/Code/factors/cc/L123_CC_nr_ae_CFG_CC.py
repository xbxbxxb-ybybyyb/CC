# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 14:10:58 2020

@author: appadmin
"""

import pandas as pd
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
import numpy as np
from operators_cc import *

class L123_CC_nr_ae_CFG_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['weight_boolean_zz500', 'low_zz500', 'turnover_zz500', 'amount_zz500']
        super(L123_CC_nr_ae_CFG_CC, self).__init__(required_columns=required_columns
                                  )

    def ts_std(self, df1, d):
        # moving time-series rank for the past d periods
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_std(df1, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=df1.index, name=df1.name)
        return output
    
    def on_bar(self, df):
        df_s = (df['amount_zz500'].rolling(120, min_periods = 15).sum())[df['weight_boolean_zz500']]
        ret_30 = (df['turnover_zz500']/df['turnover_zz500'].shift(30)-1)[df['weight_boolean_zz500']]
        temp1 = df_s.gt(pd.Series(df_s.quantile(0.80, axis = 1)), axis=0)

        temp5 = ret_30.gt(pd.Series(ret_30.quantile(0.80, axis = 1)), axis=0)
        mask = temp1*temp5
        hlow = df['low_zz500']
        i11 = (hlow.rolling(10, min_periods = 5).min()-hlow.rolling(25, min_periods = 10).min())
        i12 = hlow.rolling(20, min_periods = 15).min()-hlow.rolling(30, min_periods = 10).min()
        i2 = (i11-i12)
        ii2 = rolling_norm(i2)
        factor = (ii2*mask).sum(axis = 1).to_frame()
        factor = factor.rolling(40, min_periods = 20).mean()
        factor = ts_rank(factor)
        factor.columns = [self.__class__.__name__]
        return factor
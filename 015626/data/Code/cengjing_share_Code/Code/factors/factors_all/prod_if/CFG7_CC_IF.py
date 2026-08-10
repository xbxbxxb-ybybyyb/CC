# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 10:53:44 2021

@author: appadmin
"""
import pandas as pd
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *
import numpy as np

class CFG7_CC_IF(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['amount_hs300','open_hs300', 'weight_boolean_hs300', 'close_hs300', 'turnover_hs300', 'weight_boolean_hs300']

        super(CFG7_CC_IF, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, df):
        columnname = self.__class__.__name__
        to = df['turnover_hs300']
        hclose = df['close_hs300']
        
        hopen = df['open_hs300']
        ret = hclose/hopen -1
        hret = hclose/hclose.shift(1) -1
        ret = ret.replace([np.inf, -np.inf], np.nan)
        hret = hret.replace([np.inf, -np.inf], np.nan)
        cc1 = ((to[hclose<hopen]/abs(ret[hclose<hopen])))
        cc1[abs(cc1) > 100000] = np.nan
        ccc1 = cc1.rolling(90, min_periods = 7).mean()
        ccc1 = ccc1[df['weight_boolean_hs300']]
        hret = hret[df['weight_boolean_hs300']]
        cc2 = to_ts(ccc1, hret)
        ccc2 = cc2.rolling(90, min_periods = 15).mean()
        cc3 = rolling_norm(ccc2.to_frame(), method = 'ts_rank')
        #cc3 = cc3.rolling(3, min_periods = 2).mean()
        cc3[cc3<=-1] = np.nan
        cc3[cc3>1] = np.nan
        cc3.columns = [columnname]
        return cc3
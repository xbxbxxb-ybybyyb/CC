# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 13:49:19 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *



class CFG7_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['turnover_zz500', 'close_zz500', 'open_zz500', 'weight_boolean_zz500']

        super(CFG7_CC, self).__init__(required_columns=required_columns
                                  )
    

    def on_bar(self, df):
        columnname = self.__class__.__name__
        to = df['turnover_zz500']
        hclose = df['close_zz500']
        
        hopen = df['open_zz500']
        ret = hclose/hopen -1
        hret = hclose/hclose.shift(1) -1
        cc1 = ((to[hclose<hopen]/abs(ret[hclose<hopen])))
        ccc1 = cc1.rolling(60, min_periods = 7).mean()
        ccc1 = ccc1[df['weight_boolean_zz500']]
        hret = hret[df['weight_boolean_zz500']]
        cc2 = to_ts(ccc1, hret)
        ccc2 = cc2.rolling(60, min_periods = 15).mean()
        cc3 = rolling_norm(ccc2.to_frame(), method = 'ts_rank')
        #cc3 = cc3.rolling(3, min_periods = 2).mean()
        cc3[cc3<=-1] = np.nan
        cc3[cc3>1] = np.nan
        cc3.columns = [columnname]
        return cc3

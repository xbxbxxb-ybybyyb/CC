# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 15:00:22 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from operators_cc import *


class CFG12_CC(FactorGeneratorComplex):
    def __init__(self):
        required_columns=['close_zz500', 'low_zz500', 'weight_zz500', 'weight_boolean_zz500']
        lookback_bars=2000
        super(CFG12_CC, self).__init__(required_columns=required_columns,
                                  lookback_bars=lookback_bars)
    
    
    def on_bar(self, df):
        columnname = self.__class__.__name__

        hclose = df['close_zz500']
        hlow = df['low_zz500']
        weight = df['weight_zz500']
        g = hlow.rolling(120, min_periods = 90).min()/hclose
        g1 = ((g*weight)[df['weight_boolean_zz500']]).mean(axis = 1)
        gg1 = (-g1)
        gg2 = rolling_norm(gg1.to_frame(), method = 'ts_rank')
        #gg2[gg2<=-0.5] = np.nan
        gg2[gg2>1] = np.nan
        gg2.columns = [columnname]    
        return gg2

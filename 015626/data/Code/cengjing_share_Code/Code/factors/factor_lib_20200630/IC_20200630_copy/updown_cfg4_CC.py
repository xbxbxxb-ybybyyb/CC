# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 13:06:42 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex


# demo
class updown_cfg4_CC(FactorGeneratorComplex):
    def __init__(self):

        required_columns =['close_zz500', 'volume_zz500', 'weight_boolean_zz500']

        super(updown_cfg4_CC, self).__init__(
                                  required_columns=required_columns, lookback_bars=2000)
        
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):
        hc = (data['close_zz500']/data['close_zz500'].shift(1)-1)[data['weight_boolean_zz500']]
        hcv = (data['volume_zz500']/data['volume_zz500'].shift(1)-1)[data['weight_boolean_zz500']]
        upclose = (hc>0).sum(axis = 1)
        downclose = (hc<0).sum(axis = 1)
        upvolume = (hcv > 0).sum(axis = 1)
        downvolume = (hcv < 0).sum(axis = 1)
        vwtc_r = ((upclose/downclose)/(upvolume/downvolume)).rolling(35, min_periods = 15).mean()
        factor = vwtc_r.to_frame()
        factor.index = hc.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor


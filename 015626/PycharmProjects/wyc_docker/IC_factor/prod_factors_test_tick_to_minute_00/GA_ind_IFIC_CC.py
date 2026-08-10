# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 17:46:55 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
# demo
class GA_ind_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if', 'open_spot_if', 'high_spot_if']

        super(GA_ind_IFIC_CC, self).__init__(
                                  required_columns=required_columns)
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        n = 120
        a = data['high_spot_if'].rolling(n, min_periods = int(n/2)).max()-data['open_spot_if'].shift(n)
        b = data['close_spot_if'] - data['low_spot_if'].rolling(n, min_periods = int(n/2)).min()
        c = (data['high_spot_if'].rolling(n, min_periods = int(n/2)).max()-data['low_spot_if'].rolling(n, min_periods = int(n/2)).min())*2
        c[abs(c) < 1e-8] = np.nan
        vwtc_r = (a*b)/c
        factor = vwtc_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor[factor>1] = np.nan
        factor[factor<=-0.5] = np.nan
        return factor
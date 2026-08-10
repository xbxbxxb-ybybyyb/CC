# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 11:07:34 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator


class LCCorr_CC(FactorGenerator):
    def __init__(self):
        factor_name='LCCorr_CC'
        required_columns =['low', 'close']
        lookback_bars = 95
        super(LCCorr_CC, self).__init__(factor_name=factor_name,
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)

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
        t_chgpcor = pd.concat([data['low'], data['close']], axis = 1)
        t_chgpcor2 = t_chgpcor.rolling(40, min_periods = 15).corr(pairwise=True).unstack()
        t_chgpcor2 = t_chgpcor2[('low', 'close')]
        t_chgpcor2[t_chgpcor2 == np.inf] = 1
        factor = t_chgpcor2.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor,n=242*5)
        factor[factor<0]=np.nan
        return factor

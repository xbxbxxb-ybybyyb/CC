# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:42:21 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

def ts_rank(test, n=1200):
    a = bk.move_rank(test.iloc[:,0], n, min_count=int(n/2))
    aa = pd.DataFrame(a)
    aa.index = test.index
    aa.columns = test.columns
    return aa

class HMaxHmean_CC(FactorGenerator):
    def __init__(self):
        required_columns =['high']
        super(HMaxHmean_CC, self).__init__(
                                  required_columns=required_columns)
    
    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        ctl_r = data['high'].rolling(40, min_periods = 10).max()/data['high'].rolling(40, min_periods = 10).min()
        factor = ctl_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor,n=242*3)
        return factor


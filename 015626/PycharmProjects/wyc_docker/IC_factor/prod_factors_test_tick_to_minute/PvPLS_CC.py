# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 14:17:00 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class PvPLS_CC(FactorGenerator):
    def __init__(self):

        required_columns =['position']

        super(PvPLS_CC, self).__init__(
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
        temp1 = data['position'].rolling(20, min_periods = 15).max()
        temp2 = data['position'].rolling(20, min_periods = 15).min()
        temp3 = temp1-temp2
        temp3[abs(temp3)<1e-8] = np.nan
        t_prcd2 = -(data['position']/temp3).rolling(3, min_periods = 2).mean()
        factor = t_prcd2.to_frame()

        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
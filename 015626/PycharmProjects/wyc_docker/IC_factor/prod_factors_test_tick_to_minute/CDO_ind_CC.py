# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 12:20:34 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class CDO_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['open_spot', 'close_spot']

        super(CDO_ind_CC, self).__init__(
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
        odc_ind_r = data['close_spot'].rolling(150, min_periods = 60).mean()-data['open_spot'].rolling(150, min_periods = 60).mean()
        factor = odc_ind_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor, 242*4)
        factor[factor<=-0.5] = np.nan
        factor[factor>1] = np.nan
        return factor

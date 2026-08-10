# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 14:40:35 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class Absvc_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'volume']
        super(Absvc_CC, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa

    def on_bar(self, data):
        idx = data.index
        data = data.loc[~(((idx.hour==9) & (idx.minute < 30)) | ((idx.hour==11) & (idx.minute == 30)))]
        data = data.sort_index()
        temp1 = data['close'].diff()
        temp2 = np.abs(data['volume'] * temp1)
        hdl_ind_r = temp2.rolling(20, min_periods = 10).mean()
        factor = hdl_ind_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        return factor
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 16:42:14 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class HLTM_Aug_ind_ICIF_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot', 'high_spot', 'low_spot', 'volume_spot']

        super(HLTM_Aug_ind_ICIF_CC_IF, self).__init__(
                                  required_columns=required_columns)

    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    def on_bar(self, data):

        temp1 = data['high_spot'].rolling(15, min_periods = 7).max()-data['close_spot']
        temp2 = data['close_spot']-data['low_spot'].rolling(15, min_periods = 7).min()
        temp = pd.Series(np.where(temp1>temp2, temp1, temp2))
        temp.index = data['high_spot'].index
        vwtc_r = (temp*data['volume_spot']).rolling(35, min_periods = 10).mean()
        
        factor = vwtc_r.to_frame()
        

        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor, 242*5)
        return factor

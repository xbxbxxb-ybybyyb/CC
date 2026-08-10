# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 09:18:46 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator

class CDO_CC(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open']
        super(CDO_CC, self).__init__(required_columns=required_columns)
                                 
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
        cdo_r = data['close'].rolling(120, min_periods = 60).mean()/data['open'].rolling(120, min_periods = 60).mean()
        factor = cdo_r.to_frame()
        factor.index = data.index
        factor.columns = [self.__class__.__name__]
        factor = self.ts_rank(factor)
        factor = factor.rolling(3,min_periods=1).mean()
        factor[factor<=-0.5]=np.nan
        return factor


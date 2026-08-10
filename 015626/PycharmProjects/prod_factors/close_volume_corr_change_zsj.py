# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""

class close_volume_corr_change_zsj(FactorGenerator):
    def __init__(self):
        super(close_volume_corr_change_zsj, self).__init__(factor_name = 'close_volume_corr_change_zsj',
                                                required_columns = [ 'close','volume'],
                                                lookback_bars = 300)
    
    def ts_rank(self, test, n=1200):
        a = bk.move_rank(test.iloc[:,0], n, min_count=1)
        aa = pd.DataFrame(a)
        aa.index = test.index
        aa.columns = test.columns
        return aa
    
    def on_bar(self, data):
        ##### def data #####


        ##### calc factor #####
        df = data.loc[:, ['volume', 'close']]     
        df_corr = -df.rolling(30, min_periods = 15).corr(pairwise=True).unstack()
        df_corr = df_corr[('volume', 'close')]
        df_corr[df_corr == np.inf] = np.nan
        
        
        close_volume_corr_change = df_corr.rolling(8, min_periods = 2).mean()
        
        ##### format factor #####
        close_volume_corr_change.name = self.__class__.__name__
        factor = pd.DataFrame(close_volume_corr_change)
        factor = self.ts_rank(factor)
        factor[factor<=-0.5] = np.nan
        return factor


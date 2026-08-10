# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 17:46:40 2020

@author: appadmin
"""

from operators_cc import *
import pandas as pd
from factor_generator import FactorGenerator
import numpy as np

class CC_12(FactorGenerator):
    def __init__(self):
        required_columns=['high_spot', 'close_spot']

        super(CC_12, self).__init__(required_columns=required_columns)

            
    def on_bar(self, data):
        high = data['high_spot']
        close = data['close_spot']
        s = high.rolling(60, min_periods=30).std()
        f = close.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-8] = np.nan
        f[abs(f) < 1e-8] = np.nan
        t_pcor2 = high.rolling(60, min_periods=30).cov(close) / (s * f)

        t_pcor2[abs(t_pcor2) > 1e8] = 0
        dd1 = t_pcor2.between_time('13:00', '14:49')
        dd1 = dd1.groupby(dd1.index.date).mean()
        dd1 = ts_rank(dd1.to_frame(), 30)
        dd1.index = pd.to_datetime(dd1.index)
        dd1.index.name = 'dt'
        dd1.columns = [self.__class__.__name__]
        return dd1
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 17:19:45 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator
# demo
class GA_ind_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if', 'low_spot_if', 'open_spot_if', 'high_spot_if']

        super(GA_ind_CC_IF, self).__init__(
                                  required_columns=required_columns)

    

    def on_bar(self, data):

        n = 120
        a = data['high_spot_if'].rolling(n, min_periods = int(n/2)).max()-data['open_spot_if'].shift(n)
        b = data['close_spot_if'] - data['low_spot_if'].rolling(n, min_periods = int(n/2)).min()
        c = (data['high_spot_if'].rolling(n, min_periods = int(n/2)).max()-data['low_spot_if'].rolling(n, min_periods = int(n/2)).min())*2
        
        vwtc_r = (a*b)/c
        vwtc_r = vwtc_r.replace([-np.inf, np.inf], np.nan)
        factor = vwtc_r.to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 242*3)
        factor[factor<=-0.5] = 0
        
        return factor
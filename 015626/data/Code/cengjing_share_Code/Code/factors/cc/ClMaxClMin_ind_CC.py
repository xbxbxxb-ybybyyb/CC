# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 13:18:15 2020

@author: appadmin
"""

import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *


class ClMaxClMin_ind_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot']
 
        super(ClMaxClMin_ind_CC, self).__init__(
                                  required_columns=required_columns)
    
    def on_bar(self, data):

        m_vwap_ind_r = (data['close_spot']).rolling(60, min_periods = 30).max()/data['close_spot'].rolling(60, min_periods = 30).min()
        factor = m_vwap_ind_r.to_frame()

        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, method = 'ts_rank')
        return factor


# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 15:39:28 2020

@author: appadmin
"""

import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator

class ClMaxClMin_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close', 'recent_month_mask']
 
        super(ClMaxClMin_CC_IF, self).__init__(
                                  required_columns=required_columns)
    

        
    
        
    def on_bar(self, data):
        m_vwap_ind_r = (data['close']).rolling(40, min_periods = 30).max()/data['close'].rolling(40, min_periods = 30).min()
        factor = m_vwap_ind_r[data['recent_month_mask']].mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*2)
        factor = factor.rolling(2, min_periods = 1).mean()
        factor = ts_rank(factor)
        return factor
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 19:16:39 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class ClMaxClMin_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['close_if', 'recent_month_mask']
 
        super(ClMaxClMin_IFIC_CC, self).__init__(
                                  required_columns=required_columns)

    
    def on_bar(self, data):

        m_vwap_ind_r = (data['close_if']).rolling(30, min_periods = 15).max()/data['close_if'].rolling(30, min_periods = 15).min()
        factor = m_vwap_ind_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = rolling_norm(factor, 242*3, method = 'ts_rank')

        
        return factor



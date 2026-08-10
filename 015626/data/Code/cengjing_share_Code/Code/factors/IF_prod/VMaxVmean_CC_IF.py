# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 16:06:43 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *


from factor_generator import FactorGenerator

class VMaxVmean_CC_IF(FactorGenerator):
    def __init__(self):
        required_columns=['vwap', 'recent_month_mask']
        super(VMaxVmean_CC_IF, self).__init__(required_columns=required_columns)

        


    def on_bar(self, data):

        m_vwap_r = data['vwap'].rolling(60, min_periods = 30).max()/data['vwap'].rolling(60, min_periods = 30).min()
        factor = m_vwap_r[data['recent_month_mask']].mean(axis = 1).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, 480)
        return factor

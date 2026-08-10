# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 16:17:24 2020

@author: appadmin
"""
import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator import FactorGenerator
from operators_cc import *

class HLTM_IFIC_CC(FactorGenerator):
    def __init__(self):

        required_columns =['vwap_if', 'high_if', 'low_if', 'recent_month_mask']

        super(HLTM_IFIC_CC, self).__init__(
                                  required_columns=required_columns)


    
    def on_bar(self, data):

        temp1 = data['high_if'].rolling(15, min_periods = 7).max()-data['vwap_if']
        temp2 = data['vwap_if']-data['low_if'].rolling(15, min_periods = 7).min()
        temp = pd.DataFrame(np.where(temp1>temp2, temp1, temp2))
        temp.index = temp1.index
        temp.columns = temp1.columns
        vwtc_r = temp.rolling(40, min_periods = 15).mean() 
        factor = (vwtc_r[data['recent_month_mask']]).mean(axis = 1).to_frame()
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        return factor

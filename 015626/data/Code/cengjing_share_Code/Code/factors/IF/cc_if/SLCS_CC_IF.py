# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 15:44:39 2020

@author: appadmin
"""
import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator
import talib.abstract as ta


class SLCS_CC_IF(FactorGenerator):
    def __init__(self):

        required_columns =['close_spot_if']

        super(SLCS_CC_IF, self).__init__(
                                  required_columns=required_columns)
        

    


    
    def on_bar(self, data):


        close_spot = data['close_spot_if'].values
        
        ind = list(range(len(close_spot)))

        m_vwap_ind_r = rolling_linear_reg(ind, close_spot, 60)
        #factor = pd.Series(data['close_spot_if'].rolling(25, min_periods = 1).skew()).to_frame()
        factor = pd.Series(m_vwap_ind_r).to_frame()
        factor.index = data['close_spot_if'].index
        factor.columns = [self.__class__.__name__]

        factor = ts_rank(factor)
        factor[factor<=-0.5] = np.nan
        factor = ts_rank(factor, 242*4)
        factor[factor<=-0.5] = 0
        return factor
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 16:25:02 2020

@author: appadmin
"""

import pandas as pd
from operators_cc import *

import numpy as np

from factor_generator import FactorGenerator


class SLHS_CC_ICIF_IF(FactorGenerator):
    def __init__(self):

        required_columns =['high_spot']

        super(SLHS_CC_ICIF_IF, self).__init__(
                                  required_columns=required_columns)
        


    
    def on_bar(self, data):


        high_spot = data['high_spot'].values
        
        ind = list(range(len(high_spot)))

        m_vwap_ind_r = rolling_linear_reg(ind, high_spot, 60)
        #factor = pd.Series(data['close_spot_if'].rolling(25, min_periods = 1).skew()).to_frame()
        factor = pd.Series(m_vwap_ind_r).to_frame()
        factor.index = data['high_spot'].index
        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor)
        #factor[factor>1] = np.nan
        factor[factor<=-0.5] = np.nan
        factor = ts_rank(factor, 242*6)
        factor = ts_rank(factor)
        factor[factor<=-0.5] = 0

        return factor
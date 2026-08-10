# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:48:50 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class SLHS_CC_ICIF_IF(FutureFactor):
    
    data_type = 'Future'
    days_past = 20
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        high_spot = (data['high_000905.SH'].values)[-2730:]
        ind = list(range(len(high_spot)))
        m_vwap_ind_r = rolling_linear_reg(ind, high_spot, 60)
        factor = ts_rank(m_vwap_ind_r, 1200)
        factor[factor<=-0.5] = np.nan
        factor = ts_rank(factor, 242*6)
        
        return factor[-1]
    
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:48:34 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


    
class SLCS_CC_IF_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 7
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IF':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000016.SH':['close', 'high', 'low', 'open']}
    normalize_size = 242*4
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    
    def calculate(self, data):
        close_spot = (data['close_000016.SH'].values)[-1290:]
        ind = list(range(len(close_spot)))
        m_vwap_ind_r = rolling_linear_reg(ind, close_spot, 60)
        factor = rolling_norm(m_vwap_ind_r, method = 'ts_rank')
        factor[factor<=-0.5] = np.nan

        return factor[-1]

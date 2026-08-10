# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:46:10 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class LMLS_ind_ICIF_CC_IF_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':['low']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
#    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        low = data['low_cont_IH'].values[-90:]
        factor = np.nanmean(low[-75:]) - np.nanmean(shift(low, 30)[-45:])
        return factor
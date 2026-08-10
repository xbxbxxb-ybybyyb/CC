# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:22:51 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class IFIC4_CC_IH(FutureFactor):
  
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':[ 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    #num_range = [0, 1]
    
    def calculate(self, data):

        hclose = (data['close_000016.SH'].values)[-65:]
        temp1 = bk.move_mean(hclose, 60, min_count = 15) - bk.move_mean(shift(hclose, 20), 40, min_count =7)
        factor = np.abs(temp1)
        
        return factor[-1]
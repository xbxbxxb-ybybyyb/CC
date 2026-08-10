# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:39:32 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class cd_ind_CC_IF_IH(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close', 'open']}
    normalize_size = 4800
    normalize_type = 'rolling_norm'
#    num_range = '(-0, 1]'
    
    def calculate(self, data):
        
        hclose = data['close_000016.SH'].values[-62:]

        factor = np.diff(bk.move_mean(hclose, 60))
        
        return factor[-1]
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 15:20:23 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

    
class HcorrC_ind_IFIC_CC_IH(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['high', 'close']}
    normalize_size = 2420
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        hclose = (data['close_000016.SH']).iloc[-60:]
        hhigh = (data['high_000016.SH']).iloc[-60:]
        factor = hclose.corr(hhigh)
        return factor
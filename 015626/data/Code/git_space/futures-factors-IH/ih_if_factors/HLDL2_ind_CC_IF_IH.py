# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 13:43:31 2021

@author: appadmin
"""
import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class HLDL2_ind_CC_IF_IH(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    #data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    data_dict['Index_Id'] = {'000016.SH':['close', 'high', 'low', 'open']}
    normalize_size = 5 * 240
    normalize_type = 'rolling_norm'
#    num_range = '[-0, 1]'
    
    def calculate(self, data):
        hlow = (data['low_000016.SH'].values)[-120:]
        hhigh = (data['high_000016.SH'].values)[-120:]
        t_pcorr = (np.diff(hhigh)+np.diff(hlow))
        factor = np.nanmean(t_pcorr[-90:])
        return factor

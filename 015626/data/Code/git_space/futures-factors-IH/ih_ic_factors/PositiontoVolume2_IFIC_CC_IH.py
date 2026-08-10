# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:32:06 2021

@author: appadmin
"""


import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class PositiontoVolume2_IFIC_CC_IH(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':[ 'OpenInterest', 'volume']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = [-0.499999, 1]
    
    def calculate(self, data):

        a = (data['OpenInterest_cont_IH'].values)[-20:]
        a[abs(a) < 1e-8] = np.nan
        hvolume = (data['volume_cont_IH'].values[-20:])
        temp = hvolume/a
        factor = np.nanmean(temp)
        return factor
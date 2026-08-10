# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:02:30 2021

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class CDO_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC': ['close', 'open']} 
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    instrument_type='recent'
                   
    def calculate(self, data):
        
        hclose = data['close_cont_IC'].values[-120:]
        hopen = data['open_cont_IC'].values[-120:]
        factor = np.nanmean(hclose)/np.nanmean(hopen)

        return factor
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:09:56 2021

@author: appadmin
"""

from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class HLTM_IFIC_CC(FutureFactor):
    
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['high','low', 'vwap']} 
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = [0, 1]
    
    def calculate(self, data):
        hlow = (data['low_cont_IF'].values)[-60:]
        hhigh = (data['high_cont_IF'].values)[-60:]
        vwap =(data['vwap_cont_IF'].values)[-60:]
        temp1 = bk.move_max(hhigh, 15, min_count = 7) - vwap
        temp2 = vwap - bk.move_min(hlow, 15, min_count = 7)
        temp = np.where(temp1>temp2, temp1, temp2)
        factor = bk.move_mean(temp, 40, min_count = 15)
        return factor[-1]

# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 18:15:27 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

class HcorrC_IFIC_CC(FutureFactor):

    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close', 'high']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    instrument_type='recent'
    
    def calculate(self, data):
        hclose = (data['close_cont_IF']).iloc[-60:]
        hhigh = (data['high_cont_IF']).iloc[-60:]
        factor = hclose.corr(hhigh)
        return factor
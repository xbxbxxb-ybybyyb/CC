# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 09:31:01 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd

### 先mask再rolling
class MALS_CC_IH(FutureFactor):
    
    data_type = 'Future'
    instrument_type='recent'
    days_past = 12
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IH':[ 'close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    instrument_type='recent'
    #num_range = [0, 1]
    
    def calculate(self, data):

        hclose = (data['close_cont_IH'].values)[-2500:]
        shift_20 = shift(hclose, 20)
        shift_20[shift_20==0] = np.nan
        temp = bk.move_mean(hclose, 60, min_count = 15) -  bk.move_mean(shift_20, 40, min_count = 7)
        factor = bk.move_mean(temp, 3, min_count = 1)
        factor = np.abs(factor)
        factor = rolling_norm(factor, 2420)
        return factor[-1]
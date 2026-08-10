# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:00:50 2021

@author: appadmin
"""

import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *

class kpz_dpo_std_zsj_if(FutureFactor):

    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = '(-0.5, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        
        hclose = data['close_cont_IC'].iloc[-1348:]
        dpo_win = 45
        ma_win = 30
        #ts_pct_win = 1200
        
        def calc_dpo_sig(close, roll_win):
            dpo = close[int(roll_win / 2 + 1):] - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo   
        
        dpo_raw = calc_dpo_sig(hclose, dpo_win)[-1230:]
        dpo_std_raw = bk.move_std(dpo_raw, 30, min_count = 1, axis = 0)[-1200:]
        dpo_std_raw = bk.move_rank(dpo_std_raw, 1200, 1080, axis = 0)[-1]
        return dpo_std_raw


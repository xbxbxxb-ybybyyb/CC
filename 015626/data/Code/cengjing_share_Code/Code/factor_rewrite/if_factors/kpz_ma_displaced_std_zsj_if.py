# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:01:18 2021

@author: appadmin
"""


import numpy as np
import pandas as pd
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
#from operators_cc import *


class kpz_ma_displaced_std_zsj_if(FutureFactor):

    data_type = 'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['close', 'high', 'low', 'open']} 
    #data_dict['Index_Id'] = {'000905.SH':['close', 'high', 'low', 'open']}
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = None
    instrument_type='recent'
    
    def calculate(self, data):
        
        close = data['close_cont_IC'].iloc[-1800:]

        ##### calc factor #####

        def calc_ma_displaced(close, short_win=10, long_win=20):
            ma_close = MA(close, long_win)
            ma_displaced = REF(ma_close, short_win)
            ma_diff = close[short_win:] - ma_displaced
            return ma_diff


        short_win = 10
        long_win = 90
        score_raw = calc_ma_displaced(close, short_win, long_win)
 
        #factor = calc_std_helper(score_raw, std_win, 242*5, norm = True)
        factor = bk.move_std(score_raw, 40, min_count = 36, axis = 0)
        factor = bk.move_rank(factor, 242*5, min_count = int(242*5*0.9), axis = 0)[-1]
        return factor

# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 10:08:12 2021

@author: appadmin
"""

import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd


class vwap_ma_zsj(FutureFactor):
    
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IC':['high','low', 'close', 'volume']} 
    normalize_size = 0
    normalize_type = 'ts_rank'
    num_range = '[0, 1]'
    instrument_type='recent'
    
    def calculate(self, data):
        close = data['close_cont_IC'].iloc[-1300:]
        high = data['high_cont_IC'].iloc[-1300:]
        low = data['low_cont_IC'].iloc[-1300:]
        volume = data['volume_cont_IC'].iloc[-1300:]

        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win):
            typical = (high + low + close) / 3
            mf = volume * typical
            volume_sum = bk.move_sum(volume, roll_win, min_count = 1, axis = 0)
            volume_sum[abs(volume_sum)<1e-8] = np.nan
            mf_sum = bk.move_sum(mf, roll_win, min_count = 1, axis = 0)
            vwap_val = mf_sum / volume_sum
            vwap_diff = close - vwap_val
            return vwap_diff


        roll_win = 15
        ma_win = 60

        score_raw = calc_vwap_sig(close, high, low, volume, roll_win)
        factor = bk.move_mean(score_raw, 60, min_count = 54, axis = 0)
        factor = bk.move_rank(factor, 1200, min_count = 1080, axis = 0)[-1]
        return factor
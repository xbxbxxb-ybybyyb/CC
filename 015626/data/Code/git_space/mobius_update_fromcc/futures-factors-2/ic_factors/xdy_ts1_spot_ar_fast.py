# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 11:22:06 2022

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *

class xdy_ts1_spot_ar_fast(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['high', 'close', 'adjfactor', 'amount']
    normalize_size = 3 * 237
    normalize_type = 'ts_rank'
    handle_preadj = True
    
    def calculate(self, data):

        high = data['high_preadj'].values[-31:]
        close = data['close_preadj'].values[-30:]
        high[abs(high) < 1e-8] = np.nan
        gain_high_60 = high[1:] / high[:-1] - 1
        h_c = close / high[1:] - 1
        a = np.nanmean(h_c, axis = 0)
        a[abs(a) < 1e-8] = np.nan
        factor = gain_high_60

        a = data['amount'].iloc[-1]
        ar = a.rank(pct=True).values *2 - 1

        factor = factor * ar

        return np.nansum(factor)

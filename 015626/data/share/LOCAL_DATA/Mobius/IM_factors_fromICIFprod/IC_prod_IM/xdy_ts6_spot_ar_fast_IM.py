# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 13:28:38 2022

@author: appadmin
"""
import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
from scipy.ndimage.interpolation import shift
from operators_cc import *
import pandas as pd
from operators_wsc_1_0 import *


class xdy_ts6_spot_ar_fast_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'adjfactor', 'amount']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    handle_preadj = True
    
    def calculate(self, data):

        hclose = data['close_preadj'].values[-60:]
        gain_close_30 = hclose/r(ts_delay(hclose, 30)) - 1
        factor = (gain_close_30[-1] - (ts_delay(gain_close_30, 20))[-1] + gain_close_30[-1])

        a = data['amount'].iloc[-1]
        ar = a.rank(pct=True).values * 2 - 1

        factor = factor * ar

        return np.nansum(factor)
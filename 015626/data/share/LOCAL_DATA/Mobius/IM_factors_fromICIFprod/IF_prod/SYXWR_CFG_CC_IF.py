# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 18:31:06 2021

@author: appadmin
"""

import numpy as np
import numpy.ma as ma
from operators_cc import *
from future_factor import FutureFactor
from operators_wsc_1_0 import *
import numpy.ma as ma
import bottleneck as bk

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))
    
class SYXWR_CFG_CC_IF(FutureFactor):
    
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'low', 'high','open', 'amount']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):

        hopen = data['open'].iloc[-155:].values
        hhigh = data['high'].iloc[-155:].values
        hclose = data['close'].iloc[-155:].values
        hlow = data['low'].iloc[-155:].values

        amount = data['amount'].iloc[-100:]      
        stk_amount_rank = (2 * amount.rank(axis=1, pct=True) - 1)

        temp1 = (np.where(hopen>hclose, hopen, hclose))

        b = bk.move_mean((hhigh - temp1), 45, min_count = 15, axis = 0)
        b[abs(b)<1e-8] = np.nan
        t_pcor = (hhigh - temp1)/b
        h = bk.move_max(hhigh, 45, min_count = 15, axis = 0)
        l = bk.move_min(hlow, 45, min_count = 15, axis = 0)
        a = h-l
        t_pcor2 = (hclose-l)/a
        t_pcorr = (t_pcor2 - t_pcor)[-100:]
        t = np.nansum(t_pcorr * stk_amount_rank, axis = 1)
        factor = ts_truncated_ema_span_1(t, 95, 10)
        factor = factor[-1]

        return factor

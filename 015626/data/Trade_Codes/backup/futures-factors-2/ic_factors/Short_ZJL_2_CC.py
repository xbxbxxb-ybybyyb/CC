# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 15:24:24 2022

@author: appadmin
"""

from future_factor import FutureFactor
import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from operators_cc import *

#
def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class Short_ZJL_2_CC(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = [ 'close', 'open', 'amount']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        hclose = data['close'].iloc[-232:]
        stk_close = hclose.values[-52:]
        stk_open = data['open'].values[-52:]
        stk_turnover = data['amount'].values[-52:]
        
        ret = stk_close / stk_open - 1
        hret = hclose/hclose.shift(1)-1
        hret = hret.ewm(5).mean().values[-1]
        stk_turnover[stk_close >= stk_open] = np.nan
        ret[stk_close >= stk_open] = np.nan
        cc1 = stk_turnover / r(abs(ret))
        ccc1 = bk.move_mean(cc1, 20, 7, axis = 0)[-1]
        ccc1_mask = np.expand_dims(np.nanmedian(ccc1), axis=-1)
        hret1 = np.ma.array(hret, mask=(ccc1<=ccc1_mask))
        hret2 = np.ma.array(hret, mask=(ccc1>=ccc1_mask))
        cc2 = np.nanmean(hret1) - np.nanmean(hret2)

        return cc2
# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from utils_zsj import *


def rolling_normalize(sig, window = 100):
    sig_max = sig.rolling(window,min_periods=int(window/2)).max()
    sig_min = sig.rolling(window,min_periods=int(window/2)).min()
    return ((sig-sig_min)/(sig_max-sig_min))*2-1

class u2d_vol_ratio_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(u2d_vol_ratio_zsj, self).__init__(factor_name = 'u2d_vol_ratio_zsj',
                                              required_columns = ['close_zz500','volume_zz500'],
                                              lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        stk_close = data['close_zz500']
        stk_volume = data['volume_zz500']
        factor_name = 'u2d_vol_ratio'
        stk_ret = stk_close / stk_close.shift(1) - 1
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0
        up_vol = stk_volume[up_mask].sum(axis=1)
        down_vol = stk_volume[down_mask].sum(axis=1)
        u2d_vol_ratio_raw = up_vol / down_vol
        u2d_vol_ratio_raw = u2d_vol_ratio_raw.rolling(90,min_periods=30).mean()
        u2d_vol_ratio = rolling_normalize(u2d_vol_ratio_raw,window=242*3)
        ##### format factor #####
        factor = pd.DataFrame(u2d_vol_ratio,columns=[self.__class__.__name__])
        return factor



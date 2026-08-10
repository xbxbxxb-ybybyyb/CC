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

class vol_diff_zsj(FactorGeneratorComplex):
    def __init__(self):
        super(vol_diff_zsj, self).__init__(factor_name = 'vol_diff_zsj',
                                              required_columns = ['close_zz500','volume_zz500', 'weight_boolean_zz500'],
                                              lookback_bars = 2400)

    def on_bar(self, data):
        ##### def data #####
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_volume = data['volume_zz500']
        factor_name = 'vol_diff'
        stk_close[abs(stk_close) < 1e-8] = np.nan
        stk_ret = (stk_close / stk_close.shift(1) - 1)[bool_mask]
        up_mask = stk_ret > 0
        down_mask = stk_ret < 0
        up_vol = stk_volume[up_mask].sum(axis=1)
        down_vol = stk_volume[down_mask].sum(axis=1)
        vol_diff_raw = up_vol - down_vol
        vol_diff_raw = vol_diff_raw.rolling(60,min_periods=15).mean()
        vol_diff = rolling_norm(vol_diff_raw,window=242*5)
        # vol_diff[vol_diff<=-0.85] = 0
        ##### format factor #####
        factor = pd.DataFrame(vol_diff,columns=[self.__class__.__name__])
        return factor



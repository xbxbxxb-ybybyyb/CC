# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""

class vwap_ma_zsj(FactorGenerator):
    def __init__(self):
        super(vwap_ma_zsj, self).__init__(factor_name = 'vwap_ma_zsj',
                                          required_columns = ['close','high','low','volume', 'recent_month_mask'],
                                          lookback_bars = 1300)

    def on_bar(self, data):
        ##### def data #####
        mask = data['recent_month_mask']
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data['volume']

        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win):
            typical = (high + low + close) / 3
            mf = volume * typical
            volume_sum = SUM(volume, roll_win)
            volume_sum[abs(volume_sum)<1e-8] = np.nan
            mf_sum = SUM(mf, roll_win)
            vwap_val = mf_sum / volume_sum
            vwap_diff = close - vwap_val
            return vwap_diff

        """vwap_ma"""
        factor_name = 'vwap_ma'
        roll_win = 15
        ma_win = 60
        ts_pct_win = 1200
        score_raw = calc_vwap_sig(close, high, low, volume, roll_win)
        vwap_ma = calc_ma_helper(score_raw, ma_win, ts_pct_win)
        vwap_ma = vwap_ma[mask].sum(axis=1)

        ##### format factor #####
        vwap_ma.name = self.__class__.__name__
        factor = pd.DataFrame(vwap_ma)
        factor[factor<0]=0
        return factor
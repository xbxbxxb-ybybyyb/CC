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
class vwap_std_zsj(FactorGenerator):
    def __init__(self):
        super(vwap_std_zsj, self).__init__(factor_name = 'vwap_std_zsj',
                                                           required_columns = ['close','high','low','volume'],
                                                           lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        high = data['high']
        low = data['low']
        volume = data['volume']

        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win):
            typical = (high + low + close) / 3
            mf = volume * typical
            volume_sum = SUM(volume, roll_win)
            mf_sum = SUM(mf, roll_win)
            vwap_val = mf_sum / volume_sum
            vwap_diff = close - vwap_val
            return vwap_diff

        """vwap_ma"""
        factor_name = 'vwap_std'
        roll_win = 150
        ma_win = 30
        ts_pct_win = 242*2

        score_raw = calc_vwap_sig(close, high, low, volume, roll_win)
        vwap_std = calc_std_helper(score_raw, ma_win, ts_pct_win)

        ##### format factor #####
        vwap_std.name = self.__class__.__name__
        factor = pd.DataFrame(vwap_std)
        return factor
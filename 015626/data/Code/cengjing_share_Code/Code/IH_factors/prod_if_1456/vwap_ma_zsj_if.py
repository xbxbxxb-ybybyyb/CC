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


class vwap_ma_zsj_if(FactorGenerator):
    def __init__(self):
        super(vwap_ma_zsj_if, self).__init__(required_columns=['close_if', 'high_if', 'low_if', 'volume_if', 'recent_month_mask'],
                                             lookback_bars=1300)

    def on_bar(self, data):
        ##### def data #####
        close = data['close_if']
        high = data['high_if']
        low = data['low_if']
        volume = data['volume_if']
        mask = data['recent_month_mask']

        ##### calc factor #####
        def calc_vwap_sig(close, high, low, volume, roll_win):
            typical = (high + low + close) / 3
            mf = volume * typical
            volume_sum = SUM(volume, roll_win)
            volume_sum[abs(volume_sum) < 1e-8] = np.nan
            mf_sum = SUM(mf, roll_win)
            vwap_val = mf_sum / volume_sum
            vwap_diff = close - vwap_val
            return vwap_diff

        """vwap_ma"""
        factor_name = 'vwap_ma'
        roll_win = 10
        ma_win = 45
        ts_pct_win = 1500
        score_raw = calc_vwap_sig(close, high, low, volume, roll_win)
        vwap_ma = calc_ma_helper(score_raw, ma_win, ts_pct_win)
        vwap_ma = vwap_ma[mask].sum(axis=1)

        ##### format factor #####
        vwap_ma.name = self.__class__.__name__
        factor = pd.DataFrame(vwap_ma)
        factor[factor<=-0.5]=0
        return factor

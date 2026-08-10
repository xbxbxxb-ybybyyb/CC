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

class adtm_ma_zsj(FactorGenerator):
    def __init__(self):
        super(adtm_ma_zsj, self).__init__(factor_name = 'adtm_ma_zsj',
                                              required_columns = ['close','high','low','open'],
                                              lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        high = data['high']
        low = data['low']
        ts_open = data['open']

        def calc_adtm(ts_open, high, low, roll_win=20, hold_break=None, buy_limit=0.5, sell_limit=-0.5):
            dtm = IF(ts_open > REF(ts_open, 1), MAX(high - ts_open, ts_open - REF(ts_open, 1)), 0)
            dbm = IF(ts_open < REF(ts_open, 1), MAX(ts_open - low, REF(ts_open, 1) - ts_open), 0)
            stm = SUM(dtm, roll_win)
            sbm = SUM(dbm, roll_win)
            adtm = (stm - sbm) / MAX(stm, sbm)
            return adtm

        """adtm_ma"""
        factor_name = 'adtm_ma'
        roll_win = 20
        ma_win = 30
        ts_pct_win = 1200
        score_raw = calc_adtm(ts_open, high, low, roll_win)
        adtm_ma = calc_ma_helper(score_raw, ma_win, ts_pct_win)
        adtm_ma.name = self.__class__.__name__
        factor = pd.DataFrame(adtm_ma)
        return factor

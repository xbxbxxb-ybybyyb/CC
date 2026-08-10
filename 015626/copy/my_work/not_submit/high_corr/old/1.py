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
class dop_ma_zsj_if(FactorGenerator):
    def __init__(self):
        super(dop_ma_zsj_if, self).__init__(required_columns = ['close_if'],
                                         lookback_bars = 1500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close_if']

        ##### calc factor #####

        def calc_dpo_sig(close, roll_win):
            dpo = close - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo

        factor_name = 'dpo_ma'
        dpo_win = 180
        ma_win = 2
        ts_pct_win = 900

        dpo_raw = calc_dpo_sig(close, dpo_win)
        dpo_ma_raw = dpo_raw.rolling(ma_win, 1).mean()
        dpo_ma = calc_ts_pct(dpo_ma_raw, ts_pct_win)

        ##### format factor #####
        dpo_ma.name = self.__class__.__name__
        factor = pd.DataFrame(dpo_ma)
        factor[factor<=-0.5] = np.nan
        factor[factor>1] = np.nan
        return factor


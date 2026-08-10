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


class kpz_dpo_std_zsj_if(FactorGenerator):
    def __init__(self):
        super(kpz_dpo_std_zsj_if, self).__init__(factor_name='dpo_std_zsj',
                                                 required_columns=['close', 'recent_month_mask'],
                                                 lookback_bars=1500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        mask = data['recent_month_mask']

        ##### calc factor #####

        def calc_dpo_sig(close, roll_win):
            dpo = close - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo

        dpo_win = 45
        ma_win = 30
        ts_pct_win = 1200
        dpo_raw = calc_dpo_sig(close, dpo_win)
        dpo_std_raw = dpo_raw.rolling(ma_win, 1).std()
        dpo_std = calc_ts_pct(dpo_std_raw, ts_pct_win)
        dpo_std = dpo_std[mask].sum(axis=1)

        ##### format factor #####
        dpo_std.name = self.__class__.__name__
        factor = pd.DataFrame(dpo_std)
        factor[factor <= -0.5] = 0
        return factor

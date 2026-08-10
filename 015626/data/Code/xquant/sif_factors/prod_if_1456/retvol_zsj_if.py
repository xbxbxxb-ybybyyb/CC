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


class retvol_zsj_if(FactorGenerator):
    def __init__(self):
        super(retvol_zsj_if, self).__init__(required_columns=['close_if', 'recent_month_mask'],
                                            lookback_bars=400)

    def on_bar(self, data):
        ##### def data #####
        mask = data['recent_month_mask']
        close = data['close_if']
        minute_ret = close / close.shift(5) - 1

        ##### calc factor #####
        """retvol"""
        vol_win = 60
        ts_pct_win = 240
        retvol_raw = minute_ret.rolling(vol_win, 1).std()
        retvol = calc_ts_pct(retvol_raw, ts_pct_win)
        retvol = retvol[mask].sum(axis=1)

        ##### format factor #####
        retvol.name = self.__class__.__name__
        factor = pd.DataFrame(retvol)
        # factor[factor <= -0.5] = 0
        return factor

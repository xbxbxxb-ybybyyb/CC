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
class ma_amt_ma_zsj(FactorGenerator):
    def __init__(self):
        super(ma_amt_ma_zsj, self).__init__(factor_name = 'ma_amt_ma_zsj',
                                                           required_columns = ['close','amount'],
                                                           lookback_bars = 500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        amount = data['amount']
        ##### calc factor #####

        def calc_ma_amt(close, amount, roll_win):
            amt_ma = MA(amount, roll_win)
            amt_diff = amount - amt_ma
            return amt_diff

        factor_name = 'ma_amt_ma'
        roll_win = 90
        ma_win = 30
        ts_pct_win = 960

        score_raw = calc_ma_amt(close, amount, roll_win)
        ma_amt_ma = calc_ma_helper(score_raw, ma_win, ts_pct_win)

        ##### format factor #####
        ma_amt_ma.name = self.__class__.__name__
        factor = pd.DataFrame(ma_amt_ma)   
        factor[factor<=-0.5] = np.nan
        return factor

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

class amihund_measure_zsj(FactorGenerator):
    def __init__(self):
        super(amihund_measure_zsj, self).__init__(factor_name = 'amihund_measure_zsj',
                                                required_columns = [ 'close','amount'],
                                                lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        amount = data['amount']
        minute_ret = close / close.shift(1) - 1

        ##### calc factor #####
        ret_pos = minute_ret > 0
        amount = amount.replace({0: np.nan})
        amihund_measure_raw = minute_ret / amount

        min_pct = 0.9
        amihund_win = 90
        ts_pct_win = 1200
        amihund_measure_raw_ma = amihund_measure_raw.rolling(amihund_win, int(amihund_win * min_pct)).mean()
        amihund_measure = calc_ts_pct(amihund_measure_raw_ma, ts_pct_win)
        amihund_measure.name = self.__class__.__name__
        ##### format factor #####
        factor = pd.DataFrame(amihund_measure)
        return factor

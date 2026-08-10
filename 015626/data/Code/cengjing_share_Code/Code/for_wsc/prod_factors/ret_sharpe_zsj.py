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

class ret_sharpe_zsj(FactorGenerator):
    def __init__(self):
        super(ret_sharpe_zsj, self).__init__(factor_name = 'ret_sharpe_zsj',
                                                required_columns = [ 'close'],
                                                lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']
        minute_ret = close/close.shift(1) - 1

        ##### calc factor #####
        min_pct = 0.9
        sharpe_win = 120
        ts_pct_win = 1200
        ret_sharpe_raw = minute_ret.rolling(sharpe_win).mean() / minute_ret.rolling(sharpe_win).std()
        ret_sharpe = calc_ts_pct(ret_sharpe_raw, ts_pct_win)

        ##### format factor #####
        ret_sharpe.name = self.__class__.__name__
        factor = pd.DataFrame(ret_sharpe)  
        return factor

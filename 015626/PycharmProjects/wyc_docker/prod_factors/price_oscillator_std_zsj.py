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
class price_oscillator_std_zsj(FactorGenerator):
    def __init__(self):
        super(price_oscillator_std_zsj, self).__init__(factor_name = 'price_oscillator_std_zsj',
                                                           required_columns = ['close'],
                                                           lookback_bars = 1500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close']

        ##### calc factor #####
        def calc_price_oscillator(close, short_win, long_win):
            ema_short = EMA(close, short_win)
            ema_long = EMA(close, long_win)
            price_oscillator = (ema_short - ema_long) / ema_long * 100
            return price_oscillator

        short_win = 10
        long_win = 60
        std_win = 60
        ts_pct_win = 1200

        price_oscillator_raw = calc_price_oscillator(close, short_win, long_win)
        price_oscillator_std_raw = price_oscillator_raw.rolling(std_win, 1).std()
        price_oscillator_std = calc_ts_pct(price_oscillator_std_raw, ts_pct_win)

        ##### format factor #####
        price_oscillator_std.name = self.__class__.__name__
        factor = pd.DataFrame(price_oscillator_std)  
        return factor

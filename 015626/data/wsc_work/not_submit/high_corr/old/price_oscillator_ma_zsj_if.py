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


class price_oscillator_ma_zsj_if(FactorGenerator):
    def __init__(self):
        super(price_oscillator_ma_zsj_if, self).__init__(required_columns=['close_if'],
                                                         lookback_bars=500)

    def on_bar(self, data):
        ##### def data #####
        close = data['close_if']

        ##### calc factor #####
        def calc_price_oscillator(close, short_win, long_win):
            ema_short = EMA(close, short_win)
            ema_long = EMA(close, long_win)
            price_oscillator = (ema_short - ema_long) / ema_long * 100
            return price_oscillator

        factor_name = 'price_oscillator_ma'
        short_win = 10
        long_win = 20
        ts_pct_win = 1200
        ma_win = 30
        price_oscillator_raw = calc_price_oscillator(close, short_win, long_win)
        price_oscillator_raw_ma = price_oscillator_raw.rolling(ma_win, 1).mean()
        price_oscillator_ma = calc_ts_pct(price_oscillator_raw_ma, ts_pct_win)

        ##### format factor #####
        price_oscillator_ma.name = self.__class__.__name__
        factor = pd.DataFrame(price_oscillator_ma)
        return factor

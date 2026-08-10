import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# pos_ma_long
class fac_36(FactorGenerator):
    def __init__(self):
        required_columns=['close']

        super(fac_36, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc, ddd):
        ##### def data #####
        close = data['close']

        ##### calc factor #####
        def calc_price_oscillator(close, short_win, long_win):
            ema_short = EMA(close, short_win)
            ema_long = EMA(close, long_win)
            price_oscillator = (ema_short - ema_long) / ema_long * 100
            return price_oscillator

        factor_name = 'price_oscillator_ma'
        short_win = int(aa/2)
        long_win = bb
        ts_pct_win = ddd * 300
        ma_win = ccc
        price_oscillator_raw = calc_price_oscillator(close, short_win, long_win)
        price_oscillator_raw_ma = price_oscillator_raw.rolling(ma_win, 1).mean()
        price_oscillator_ma = calc_ts_pct(price_oscillator_raw_ma, ts_pct_win)

        ##### format factor #####
        price_oscillator_ma.name = self.__class__.__name__
        factor = pd.DataFrame(price_oscillator_ma)
        return factor

import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
from operators_all_wsc import cross_hub_num

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


# pos_ma_long
class fac_36_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'second_main_mask']

        super(fac_36_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc, ddd):
        ##### def data #####
        
        aa = 2
        bb = 8
        ccc = 3
        ddd = 2
        mask = data['second_main_mask']
        close = data['close'][mask].mean(axis = 1)
        def calc_price_oscillator(close, short_win, long_win, mask = mask):
            ema_short = ts_truncated_ema_1(close, short_win * 3, 1/(short_win + 1))
            ema_long = ts_truncated_ema_1(close, long_win * 3, 1/(long_win + 1))
            #ema_short = close.rolling(short_win, min_periods = 1).mean()
            #ema_long = close.rolling(long_win, min_periods = 1).mean()
            price_oscillator = (ema_short - ema_long) / ema_long * 100
            return price_oscillator.fillna(method = 'ffill')


        ##### calc factor #####
        factor_name = 'price_oscillator_ma'
        short_win = aa
        long_win = bb
        price_oscillator_raw = calc_price_oscillator(close, short_win, long_win)
        price_oscillator_raw_ma = price_oscillator_raw.rolling(ccc, min_periods = 1).mean()
        co = close.diff().rolling(10, min_periods = 1).std()
        co3 = close.diff().rolling(60, min_periods = 1).std()
        co2 = cross_hub_num(close, 30) + 1
        price_oscillator_ma = ts_rank((price_oscillator_raw_ma / r(co2) / r(co2) / r(co) / r(co)).fillna(method = 'ffill'), ddd * 300)
        ##### format factor #####
        price_oscillator_ma.name = self.__class__.__name__
        factor = pd.DataFrame(price_oscillator_ma)
        return factor
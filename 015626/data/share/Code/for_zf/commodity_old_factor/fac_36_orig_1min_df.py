import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
from operators_all_wsc import cross_hub_num

# pos_ma_long
class fac_36_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'second_main_mask']

        super(fac_36_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc, ddd):
        ##### def data #####
        
        aa = 5
        bb = 40
        ccc = 3
        ddd = 2
        mask = data['second_main_mask']
        close = data['close']#[mask].mean(axis = 1)
        def calc_price_oscillator(close, short_win, long_win, mask = mask):
                ema_short = close.ewm(short_win, min_periods = 1).mean()
                ema_long = close.ewm(long_win, min_periods = 1).mean()
                price_oscillator = (ema_short - ema_long) / ema_long * 100
                return price_oscillator[mask].mean(axis = 1).fillna(method = 'ffill')


        ##### calc factor #####
        factor_name = 'price_oscillator_ma'
        short_win = aa
        long_win = bb
        price_oscillator_raw = calc_price_oscillator(close, short_win, long_win)
        price_oscillator_raw_ma = price_oscillator_raw.rolling(ccc, min_periods = 1).mean()
        co = close.diff().rolling(10, min_periods = 1).std()[mask].mean(axis = 1)
        co3 = close.diff().rolling(120, min_periods = 1).std()[mask].mean(axis = 1)
        co2 = cross_hub_num(data['close'], 60)[mask].mean(axis = 1)
        price_oscillator_ma = ts_rank((price_oscillator_raw_ma / r(np.sqrt(co3)) / r(co2)).fillna(method = 'ffill'), ddd * 300)
        ##### format factor #####
        price_oscillator_ma.name = self.__class__.__name__
        factor = pd.DataFrame(price_oscillator_ma)
        return factor

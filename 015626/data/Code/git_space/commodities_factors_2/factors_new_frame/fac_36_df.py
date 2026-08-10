from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def ema_archive(factor_array,d,alpha):

    factor_array = np.array(factor_array)

    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]

    flag = np.isnan(factor_array) | np.isnan(weight)

    flag1 = np.sum(flag, axis=-1)  # 缺失值个数

    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)

    factor_array[flag] = np.nan

    weight[flag] = np.nan

    factor = nansum_np(factor_array[-d:] * weight) / nansum_np(weight) # truncate_ema_1

    return factor

    

class fac_36_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.required_columns = ['close_secmain']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 600

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 2

        self.price_oscillator_list = []

        

        

    def calculate(self, data):

        short_win = 2

        long_win = 8

        close = data['close_secmain'][-100:]

        ema_short = ema_1(close[-short_win*3:],short_win*3,1/(short_win+1))

        ema_long = ema_1(close[-long_win*3:],long_win*3,1/(long_win+1))

        price_oscillator = (ema_short - ema_long) / ema_long * 100

        self.price_oscillator_list.append(price_oscillator)  # need to fillna

        price_oscillator_raw_ma = nanmean_np(self.price_oscillator_list[-3:])



        cls_diff = close[1:] - close[:-1]

        co = nanstd_np(cls_diff[-10:],ddof = 1)

        if abs(co) < 1e-8:

            co = np.nan

        co3 = nanstd_np(cls_diff[-60:], ddof = 1)

        co2 = cross_hub_num_array(close[-70:],30) + 1

        factor = price_oscillator_raw_ma / co2 / co2 / co / co # need to fillna

        return factor



    def pre_calculate(self, data):
        self.price_oscillator_list = []

        short_win = 2

        long_win = 8

        for i in range(3):

            if i == 0:

                close = data['close_secmain'][-100:]

            else:

                close = data['close_secmain'][-(100+i):-i]

            ema_short = ema_1(close[-short_win*3:],short_win*3,1/(short_win+1))

            ema_long = ema_1(close[-long_win*3:],long_win*3,1/(long_win+1))

            price_oscillator = (ema_short - ema_long) / ema_long * 100

            self.price_oscillator_list.append(price_oscillator)

        self.price_oscillator_list.reverse()
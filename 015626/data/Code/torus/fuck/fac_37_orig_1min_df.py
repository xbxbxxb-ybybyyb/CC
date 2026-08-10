from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

   

import numpy as np





class fac_37_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.required_columns = ['close']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = 900

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 2

        self.prefactor_list = []

        

        

    def calculate(self, data):        

        coef = int(self.bars_dict[self.ticker] / self.freq)

        sharpe_win = int(coef / 2)

        w = max(sharpe_win+30,150)

        close = data['close'][-w:]

        minute_ret = close[15:] - close[:-15]

        temp1 = nanmean_np(minute_ret[-sharpe_win:])        

        temp2 = nanmedian_np(minute_ret[-sharpe_win:])

        temp = temp1 * 2 + temp2

        minute_ret_std = nanstd_np(minute_ret[-int(sharpe_win / 2):], ddof = 1)

        if abs(minute_ret_std) < 1e-8:

            minute_ret_std = np.nan

        prefactor = temp / minute_ret_std

        self.prefactor_list.append(prefactor)

        factor = nanmean_np(self.prefactor_list[-3:])

        return factor



    def pre_calculate(self, data):

        coef = int(self.bars_dict[self.ticker] / self.freq)

        sharpe_win = int(coef / 2)

        w = max(sharpe_win + 30,150)

        for i in range(3):

            if i == 0:

                close = data['close'][-w:]

            else:

                close = data['close'][-(w+i):-i]

            minute_ret = close[15:] - close[:-15]

            temp1 = nanmean_np(minute_ret[-sharpe_win:])

            temp2 = nanmedian_np(minute_ret[-sharpe_win:])

            temp = temp1 * 2 + temp2

            minute_ret_std = nanstd_np(minute_ret[-int(sharpe_win / 2):], ddof = 1)

            if abs(minute_ret_std) < 1e-8:

                minute_ret_std = np.nan

            prefactor = temp / minute_ret_std

            self.prefactor_list.append(prefactor)

        self.prefactor_list.reverse()

            
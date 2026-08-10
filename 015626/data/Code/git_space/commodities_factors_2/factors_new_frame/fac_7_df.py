from rolling_adj import *

import numpy as np
from commodity_framework import FutureFactor


def ema_archive(factor_array, d, alpha):
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    flag = np.isnan(factor_array) | np.isnan(weight)
    factor_array[flag] = np.nan
    weight[flag] = np.nan
    factor = nansum_np(factor_array[-d:] * weight) / nansum_np(weight)
    return factor


def ema_span_1(factor_array, d, span):
    return ema_1(factor_array, d=d, alpha=2 / (span + 1))


def calculate_aroon(price_high, price_low, time_period):
    price_aroon_up = 1 + np.argmax(price_high[-time_period:])
    price_aroon_down = 1 + np.argmin(price_low[-time_period:])
    price_aroon = price_aroon_up - price_aroon_down
    return price_aroon


class fac_7_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['high', 'low']
        self.normalize_size = 1
        self.normalize_type = 'ts_rank'

        self.ch1_list = []
        self.cl1_list = []
        self.ch2_list = []
        self.cl2_list = []
        self.ch1_ema_list = []
        self.cl1_ema_list = []
        self.ch2_ema_list = []
        self.cl2_ema_list = []

    def calculate(self, data):
        h = data['high']
        l = data['low']

        aaa1 = 20
        bbb1 = 5
        aaa2 = 60
        bbb2 = 15
        ccc = 4

        c = (h + l) / 2
        ch1 = c[-1] / nanmax_np(h[-int(aaa1 / 2):]) - 1
        cl1 = c[-1] / nanmin_np(l[-int(aaa1 * 2):]) - 1
        self.ch1_list.append(ch1)
        self.cl1_list.append(cl1)
        ch1_ema = ema_span_1(np.array(self.ch1_list[-(bbb1 * 4):]), bbb1 * 4, bbb1)
        cl1_ema = ema_span_1(np.array(self.cl1_list[-(bbb1 * 4):]), bbb1 * 4, bbb1)
        self.ch1_ema_list.append(ch1_ema)
        self.cl1_ema_list.append(cl1_ema)

        ch2 = c[-1] / nanmax_np(h[-int(aaa2 / 2):]) - 1
        cl2 = c[-1] / nanmin_np(l[-int(aaa2 * 2):]) - 1
        self.ch2_list.append(ch2)
        self.cl2_list.append(cl2)
        ch2_ema = ema_span_1(np.array(self.ch2_list[-(bbb2 * 4):]), bbb2 * 4, bbb2)
        cl2_ema = ema_span_1(np.array(self.cl2_list[-(bbb2 * 4):]), bbb2 * 4, bbb2)
        self.ch2_ema_list.append(ch2_ema)
        self.cl2_ema_list.append(cl2_ema)

        fac1 = calculate_aroon(np.array(self.ch1_ema_list[-5:]), np.array(self.cl1_ema_list[-5:]), ccc)
        fac2 = calculate_aroon(np.array(self.ch2_ema_list[-5:]), np.array(self.cl2_ema_list[-5:]), ccc)
        sig = (fac1 + 2 * fac2) / 2
        return sig

    def pre_calculate(self, data):
        self.ch1_list = []
        self.cl1_list = []
        self.ch2_list = []
        self.cl2_list = []
        self.ch1_ema_list = []
        self.cl1_ema_list = []
        self.ch2_ema_list = []
        self.cl2_ema_list = []
        h_all = data['high']
        l_all = data['low']

        aaa1 = 20
        bbb1 = 5
        aaa2 = 60
        bbb2 = 15

        n = 70
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                h = h_all
                l = l_all
            else:
                h = h_all[:-j]
                l = l_all[:-j]

            c = (h + l) / 2
            if len(c) > 1:
                ch1 = c[-1] / nanmax_np(h[-int(aaa1 / 2):]) - 1
                cl1 = c[-1] / nanmin_np(l[-int(aaa1 * 2):]) - 1
            else:
                ch1 = np.nan
                cl1 = np.nan
            self.ch1_list.append(ch1)
            self.cl1_list.append(cl1)
            if (len(self.ch1_list) >= bbb1 * 4) and (len(self.cl1_list) >= bbb1 * 4):
                ch1_ema = ema_span_1(np.array(self.ch1_list[-(bbb1 * 4):]), bbb1 * 4, bbb1)
                cl1_ema = ema_span_1(np.array(self.cl1_list[-(bbb1 * 4):]), bbb1 * 4, bbb1)
                self.ch1_ema_list.append(ch1_ema)
                self.cl1_ema_list.append(cl1_ema)

            if len(c) > 1:
                ch2 = c[-1] / nanmax_np(h[-int(aaa2 / 2):]) - 1
                cl2 = c[-1] / nanmin_np(l[-int(aaa2 * 2):]) - 1
            else:
                ch2 = np.nan
                cl2 = np.nan
            self.ch2_list.append(ch2)
            self.cl2_list.append(cl2)
            if (len(self.ch2_list) >= bbb2 * 4) and (len(self.cl2_list) >= bbb2 * 4):
                ch2_ema = ema_span_1(np.array(self.ch2_list[-(bbb2 * 4):]), bbb2 * 4, bbb2)
                cl2_ema = ema_span_1(np.array(self.cl2_list[-(bbb2 * 4):]), bbb2 * 4, bbb2)
                self.ch2_ema_list.append(ch2_ema)
                self.cl2_ema_list.append(cl2_ema)

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


class fac_7_aug_orig_1min_df_5x_(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 5 * self.freq
        self.required_columns = ['high', 'low']
        self.normalize_size = 75 * 50
        self.normalize_type = 'ts_rank'

        self.ch_list = []
        self.cl_list = []
        self.hl_list = []

    def calculate(self, data):
        h = data['high']
        l = data['low']

        aaa = 150
        bbb = 25
        ccc = 5

        c = (h + l) / 2
        ch = c[-1] / nanmax_np(h[-int(aaa / 2):]) - 1
        cl = c[-1] / nanmin_np(l[-int(aaa * 2):]) - 1
        self.ch_list.append(ch)
        self.cl_list.append(cl)
        ch_ema = ema_span_1(np.array(self.ch_list[-(bbb * 4):]), bbb * 4, bbb)
        cl_ema = ema_span_1(np.array(self.cl_list[-(bbb * 4):]), bbb * 4, bbb)
        hl = ch_ema + cl_ema
        self.hl_list.append(hl)
        sig = ema_1(np.array(self.hl_list[-ccc:]), ccc, 1 / 3)
        return sig

    def pre_calculate(self, data):
        h_all = data['high']
        l_all = data['low']

        aaa = 150
        bbb = 25

        n = 150
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                h = h_all
                l = l_all
            else:
                h = h_all[:-j]
                l = l_all[:-j]

            if len(h) > 0:

                c = (h + l) / 2
                ch = c[-1] / nanmax_np(h[-int(aaa / 2):]) - 1
                cl = c[-1] / nanmin_np(l[-int(aaa * 2):]) - 1
                self.ch_list.append(ch)
                self.cl_list.append(cl)
                if (len(self.ch_list) >= bbb * 4) and (len(self.cl_list) >= bbb * 4):
                    ch_ema = ema_span_1(np.array(self.ch_list[-(bbb * 4):]), bbb * 4, bbb)
                    cl_ema = ema_span_1(np.array(self.cl_list[-(bbb * 4):]), bbb * 4, bbb)
                    hl = ch_ema + cl_ema
                    self.hl_list.append(hl)

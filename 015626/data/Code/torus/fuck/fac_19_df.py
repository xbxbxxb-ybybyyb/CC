from rolling_adj import *

import numpy as np
from commodity_framework import FutureFactor


def replace_zero(x):
    if isinstance(x, float):
        if np.abs(x) < 1e-8:
            x = np.nan
    elif isinstance(x, np.ndarray):
        x = np.where(np.abs(x) > 1e-8, x, np.nan)
    else:
        raise TypeError(type(x))
    return x


def ema_archive(factor_array, d, alpha):
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    flag = np.isnan(factor_array) | np.isnan(weight)
    factor_array[flag] = np.nan
    weight[flag] = np.nan
    factor = nansum_np(factor_array[-d:] * weight) / nansum_np(weight)
    return factor


def rank_data(data):
    n = len(data)
    if n < 1:
        return np.nan
    elif n == 1:
        return 0.0
    data = np.array(data)
    current_value = data[-1]
    less = np.sum(data < current_value)
    equal = np.sum(data == current_value)
    rank = less + (equal + 1) / 2
    return 2 * ((rank - 1) / (n - 1)) - 1


class fac_19_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 10 * self.freq
        self.required_columns = ['close', 'open']
        self.normalize_size = 1
        self.normalize_type = 'ts_rank'

        self.sig_list = []
        self.sig_ema_list = []
        self.sig_rank_list = []

    def calculate(self, data):
        c = data['close']
        o = data['open']

        aaa = 2
        bbb = 20

        cdo_r = nanmean_np(c[-aaa:]) - nanmean_np(o[-aaa:])
        self.sig_list.append(cdo_r)
        sig_ema = ema_1(np.array(self.sig_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        self.sig_ema_list.append(sig_ema)
        sig_rank = rank_data(np.array(self.sig_ema_list[-500:]))
        self.sig_rank_list.append(sig_rank)
        cs = corrcoef_np(np.array(self.sig_rank_list[-self.bars:]), c[-self.bars:])[0, 1]
        cl = corrcoef_np(np.array(self.sig_rank_list[-(self.bars * 3):]), c[-(self.bars * 3):])[0, 1]
        if (cs < cl) or (cl < 0):
            sig = 0
        else:
            sig = sig_rank
        return sig

    def pre_calculate(self, data):
        c_all = data['close']
        o_all = data['open']

        aaa = 2
        bbb = 20

        n = bbb * 3 + 500 + self.bars * 3
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                o = o_all
            else:
                c = c_all[:-j]
                o = o_all[:-j]

            cdo_r = nanmean_np(c[-aaa:]) - nanmean_np(o[-aaa:])
            self.sig_list.append(cdo_r)
            if len(self.sig_list) >= bbb * 3:
                sig_ema = ema_1(np.array(self.sig_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
                self.sig_ema_list.append(sig_ema)
            if len(self.sig_ema_list) >= 500:
                sig_rank = rank_data(np.array(self.sig_ema_list[-500:]))
                self.sig_rank_list.append(sig_rank)

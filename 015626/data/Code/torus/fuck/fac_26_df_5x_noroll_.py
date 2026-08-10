from rolling_adj import *

import numpy as np
from commodity_framework import FutureFactor


def replace_zero(x):
    if isinstance(x, float):
        if np.abs(x) < 1e-8:
            x = np.nan
    elif isinstance(x, np.ndarray):
        x = np.where(np.abs(x) < 1e-8, np.nan, x)
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


class fac_26_df_5x_noroll_(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 20 * self.freq
        self.required_columns = ['close_secmain', 'high_secmain', 'low_secmain']
        self.normalize_size = 1
        self.normalize_type = 'ts_rank'

        self.sig_list = []
        self.sig_rank_list = []

    def calculate(self, data):
        c = data['close_secmain']
        h = data['high_secmain']
        l = data['low_secmain']

        aaa = 450
        bbb = 5
        ccc = 5
        ddd = 10

        index_typical = c + h + l
        index_typical_r = (index_typical[ccc:] - index_typical[ccc - 1:-1]) / index_typical[:-ccc]
        sig_ema1 = ema_1(index_typical_r[-(aaa * 3):], aaa * 3, 1 / (aaa + 1))
        sig_ema2 = ema_1(np.abs(index_typical_r[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        sig = sig_ema1 / replace_zero(sig_ema2)
        vol = nanstd_np(index_typical[-60:], ddof=1)
        sig = sig / replace_zero(vol)
        self.sig_list.append(sig)

        sig_rank = rank_data(np.array(self.sig_list[-(ddd * 300):]))
        self.sig_rank_list.append(sig_rank)

        cs = corrcoef_np(np.array(self.sig_rank_list[-(self.bars * 1):]), index_typical[-(self.bars * 1):])[0][1]
        cl = corrcoef_np(np.array(self.sig_rank_list[-(self.bars * 4):]), index_typical[-(self.bars * 4):])[0][1]
        if (cs < cl) or (cs < 0):
            sig = 0.0
        else:
            sig = sig_rank
        return sig

    def pre_calculate(self, data):
        c_all = data['close_secmain']
        h_all = data['high_secmain']
        l_all = data['low_secmain']

        aaa = 450
        bbb = 5
        ccc = 5
        ddd = 10

        n = self.bars * 4 + ddd * 300
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                h = h_all
                l = l_all
            else:
                c = c_all[:-j]
                h = h_all[:-j]
                l = l_all[:-j]

            index_typical = c + h + l
            index_typical_r = (index_typical[ccc:] - index_typical[ccc - 1:-1]) / index_typical[:-ccc]
            sig_ema1 = ema_1(index_typical_r[-(aaa * 3):], aaa * 3, 1 / (aaa + 1))
            sig_ema2 = ema_1(np.abs(index_typical_r[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
            sig = sig_ema1 / replace_zero(sig_ema2)
            vol = nanstd_np(index_typical[-60:], ddof=1)
            sig = sig / replace_zero(vol)
            self.sig_list.append(sig)

            if len(self.sig_list) >= ddd * 300:
                sig_rank = rank_data(np.array(self.sig_list[-(ddd * 300):]))
                self.sig_rank_list.append(sig_rank)

from rolling_adj import *

import numpy as np
import bottleneck as bk
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


def cross_hub_num_array(data_array, d):
    data_centralized = data_array - move_mean_bk(data_array, window=d, min_count=int(d / 2))
    flag = (data_centralized[1:] * data_centralized[:-1]) < 0
    output = np.sum(flag[-d:])
    return output


class fac_26_orig_1min_df_10x_(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 20 * self.freq
        self.required_columns = ['close_secmain', 'high_secmain', 'low_secmain']
        self.normalize_size = 50 * 300
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close_secmain']
        h = data['high_secmain']
        l = data['low_secmain']

        aaa = 700
        bbb = 700
        ccc = 100

        index_typical = c + h + l
        index_typical_r = (index_typical[1:] - index_typical[:-1]) / index_typical[:-1]
        sig_ema1 = ema_1(index_typical_r[-(aaa * 3):], aaa * 3, 1 / (aaa + 1))
        sig_ema2 = ema_1(np.abs(index_typical_r[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        sig = sig_ema1 / replace_zero(sig_ema2)
        self.sig_list.append(sig)

        co = cross_hub_num_array(index_typical, aaa) + 1.0
        vol = nanstd_np(index_typical[-aaa:], ddof=1)
        sig = ema_1(np.array(self.sig_list[-(ccc * 3):]), ccc * 3, 1 / (ccc + 1)) / replace_zero(co) / np.sqrt(replace_zero(vol))
        return sig

    def pre_calculate(self, data):
        c_all = data['close_secmain']
        h_all = data['high_secmain']
        l_all = data['low_secmain']

        aaa = 700
        bbb = 700
        ccc = 100

        n = ccc * 3
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
            index_typical_r = (index_typical[1:] - index_typical[:-1]) / index_typical[:-1]
            sig_ema1 = ema_1(index_typical_r[-(aaa * 3):], aaa * 3, 1 / (aaa + 1))
            sig_ema2 = ema_1(np.abs(index_typical_r[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
            sig = sig_ema1 / replace_zero(sig_ema2)
            self.sig_list.append(sig)

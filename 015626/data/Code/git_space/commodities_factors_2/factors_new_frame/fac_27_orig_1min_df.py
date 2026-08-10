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


class fac_27_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['close_secmain', 'high_secmain', 'low_secmain']
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close_secmain']
        h = data['high_secmain']
        l = data['low_secmain']

        aaa = 30
        bbb = 100
        ccc = 20

        if bbb < 100:
            bbb_temp = nanmax_np([int(aaa * bbb / 100), 1])
        elif (bbb >= 100) and (bbb < 200):
            bbb_temp = int(aaa / 3)
        else:
            bbb_temp = int(aaa * 2 / 3)

        temp1 = nanmean_np(l[-aaa:]) - nanmean_np(l[-aaa:-bbb_temp])
        temp2 = nanmean_np(h[-aaa:]) - nanmean_np(h[-aaa:-bbb_temp])
        temp = temp1 + temp2
        co = nanstd_np(c[-30:], ddof=1)
        co2 = cross_hub_num_array(c, aaa) + 1.0
        sig = temp / replace_zero(co) / replace_zero(co2)
        self.sig_list.append(sig)
        sig = ema_1(np.array(self.sig_list[-(ccc * 3):]), ccc * 3, 1 / (ccc + 1))
        return sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close_secmain']
        h_all = data['high_secmain']
        l_all = data['low_secmain']

        aaa = 30
        bbb = 100
        ccc = 20

        if bbb < 100:
            bbb_temp = nanmax_np([int(aaa * bbb / 100), 1])
        elif (bbb >= 100) and (bbb < 200):
            bbb_temp = int(aaa / 3)
        else:
            bbb_temp = int(aaa * 2 / 3)

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

            temp1 = nanmean_np(l[-aaa:]) - nanmean_np(l[-aaa:-bbb_temp])
            temp2 = nanmean_np(h[-aaa:]) - nanmean_np(h[-aaa:-bbb_temp])
            temp = temp1 + temp2
            co = nanstd_np(c[-30:], ddof=1)
            co2 = cross_hub_num_array(c, aaa) + 1.0
            sig = temp / replace_zero(co) / replace_zero(co2)
            self.sig_list.append(sig)

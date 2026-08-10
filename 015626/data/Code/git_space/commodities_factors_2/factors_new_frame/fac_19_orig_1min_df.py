from rolling_adj import *

import numpy as np
import bottleneck as bk
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


def cross_hub_num_array(data_array, d):
    data_centralized = data_array - move_mean_bk(data_array, window=d, min_count=int(d / 2))
    flag = (data_centralized[1:] * data_centralized[:-1]) < 0
    output = np.sum(flag[-d:])
    return output


class fac_19_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'open']
        self.normalize_size = 500
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        o = data['open']

        aaa = 10
        bbb = 70

        cdo_r = nanmean_np(c[-aaa:]) - nanmean_np(o[-aaa:])
        co = cross_hub_num_array(c, aaa) + 1.0
        cdo_r = cdo_r / replace_zero(np.sqrt(co))
        self.sig_list.append(cdo_r)
        sig = ema_1(np.array(self.sig_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        return sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close']
        o_all = data['open']

        aaa = 10
        bbb = 70

        n = bbb * 3
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                o = o_all
            else:
                c = c_all[:-j]
                o = o_all[:-j]

            cdo_r = nanmean_np(c[-aaa:]) - nanmean_np(o[-aaa:])
            co = cross_hub_num_array(c, aaa) + 1.0
            cdo_r = cdo_r / replace_zero(np.sqrt(co))
            self.sig_list.append(cdo_r)

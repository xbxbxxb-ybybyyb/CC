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


class fac_30_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'low']
        self.normalize_size = 1500
        self.normalize_type = 'ts_rank'

        self.lm_list = []
        self.lltc_list = []

    def calculate(self, data):
        c = data['close']
        l = data['low']

        aaa = 20
        bbb = 4

        lm = nanmean_np(l[-3:])
        self.lm_list.append(lm)

        ll = nanmin_np(np.array(self.lm_list[-aaa:]))
        lltc = c[-1] - ll
        self.lltc_list.append(lltc)

        c_diff = c[1:] - c[:-1]
        co = nanstd_np(c_diff[-10:], ddof=1)
        co2 = cross_hub_num_array(c, 10) + 1.0
        sig = lltc + 1.5 * nanmean_np(np.array(self.lltc_list[-bbb:]))
        sig = sig / replace_zero(co) / np.sqrt(replace_zero(co2))
        return sig

    def pre_calculate(self, data):
        self.lm_list = []
        self.lltc_list = []
        c_all = data['close']
        l_all = data['low']

        aaa = 20
        bbb = 4

        n = aaa + bbb
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                l = l_all
            else:
                c = c_all[:-j]
                l = l_all[:-j]
            if len(c) >= 1:
                lm = nanmean_np(l[-3:])
                self.lm_list.append(lm)

                if len(self.lm_list) >= aaa:
                    ll = nanmin_np(np.array(self.lm_list[-aaa:]))
                    lltc = c[-1] - ll
                    self.lltc_list.append(lltc)
            else:
                self.lm_list.append(np.nan)
                self.lltc_list.append(np.nan)

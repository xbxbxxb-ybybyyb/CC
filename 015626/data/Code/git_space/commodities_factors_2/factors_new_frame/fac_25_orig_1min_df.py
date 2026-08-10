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


class fac_25_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close_secmain', 'volume_secmain']
        self.normalize_size = 6000
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close_secmain']
        v = data['volume_secmain']

        aaa = 12
        bbb = 90
        ccc = 8

        ret = c[aaa:] - c[:-aaa]
        c_diff = c[1:] - c[:-1]
        ret_std = nanstd_np(c_diff[-bbb:], ddof=1)
        sig = ret[-1] * ret_std * nanmean_np(v[-aaa:])
        self.sig_list.append(sig)
        sig = ema_1(np.array(self.sig_list[-(ccc * 3):]), ccc * 3, 1 / (ccc + 1))
        return sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close_secmain']
        v_all = data['volume_secmain']

        aaa = 12
        bbb = 90
        ccc = 8

        n = ccc * 3
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                v = v_all
            else:
                c = c_all[:-j]
                v = v_all[:-j]
            if len(c) > 1:
                ret = c[aaa:] - c[:-aaa]
                c_diff = c[1:] - c[:-1]
                ret_std = nanstd_np(c_diff[-bbb:], ddof=1)
                sig = ret[-1] * ret_std * nanmean_np(v[-aaa:])
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)

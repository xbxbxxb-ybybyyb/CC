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


class fac_24_2_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['close', 'high']
        self.normalize_size = 10 * 300
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']

        aaa = 20
        bbb = 90

        hc_corr = corrcoef_np(h[-aaa:], c[-aaa:])[0][1]
        hc_corr = np.where(np.isfinite(hc_corr), hc_corr, 0)
        c_diff = c[-1] - c[-1 - 5]
        sig = hc_corr * np.sqrt(np.sqrt(np.abs(c_diff))) * np.sign(c_diff)
        self.sig_list.append(sig)
        sig = ema_1(np.array(self.sig_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        return sig

    def pre_calculate(self, data):
        self.sig_list = []
        c_all = data['close']
        h_all = data['high']

        aaa = 20
        bbb = 90

        n = bbb * 3
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                h = h_all
            else:
                c = c_all[:-j]
                h = h_all[:-j]
            if len(c) > 6:
                hc_corr = corrcoef_np(h[-aaa:], c[-aaa:])[0][1]
                hc_corr = np.where(np.isfinite(hc_corr), hc_corr, 0)
                c_diff = c[-1] - c[-1 - 5]
                sig = hc_corr * np.sqrt(np.sqrt(np.abs(c_diff))) * np.sign(c_diff)
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)

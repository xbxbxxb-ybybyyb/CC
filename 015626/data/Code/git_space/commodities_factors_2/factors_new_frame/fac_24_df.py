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


class fac_24_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['close', 'high']
        self.normalize_size = 5 * 300
        self.normalize_type = 'ts_rank'

        self.corr_list = []
        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']

        aaa = 6
        bbb = 30

        hc_corr = corrcoef_np(h[-aaa:], c[-aaa:])[0][1]
        if np.isnan(hc_corr) and len(self.corr_list) > 0:
            hc_corr = self.corr_list[-1]
        if np.isnan(hc_corr) or np.isinf(hc_corr):
            hc_corr = 0.0
        self.corr_list.append(hc_corr)

        c_diff = c[-1] - c[-1 - 5]
        sig = hc_corr * np.sign(c_diff)
        self.sig_list.append(sig)

        sig = ema_1(np.array(self.sig_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        co1 = cross_hub_num_array(c, 20) + 1.0
        co2 = nanstd_np(np.array(self.sig_list[-120:]), ddof=1)
        c_diff = c[1:] - c[:-1]
        vol1 = nanstd_np(c_diff[-10:], ddof=1)
        vol2 = nanstd_np(c_diff[-30:], ddof=1)
        sig = sig / replace_zero(co1) / replace_zero(co2) / replace_zero(vol1) / replace_zero(vol2)
        return sig

    def pre_calculate(self, data):
        self.corr_list = []
        self.sig_list = []
        c_all = data['close']
        h_all = data['high']

        aaa = 6
        bbb = 30

        n = bbb * 3
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                h = h_all
            else:
                c = c_all[:-j]
                h = h_all[:-j]

            hc_corr = corrcoef_np(h[-aaa:], c[-aaa:])[0][1]
            if np.isnan(hc_corr) and len(self.corr_list) > 0:
                hc_corr = self.corr_list[-1]
            if np.isnan(hc_corr) or np.isinf(hc_corr):
                hc_corr = 0.0
            self.corr_list.append(hc_corr)
            if len(c) >= 6:
                c_diff = c[-1] - c[-1 - 5]
                sig = hc_corr * np.sign(c_diff)
                self.sig_list.append(sig)
            else:
                self.sig_list.append(np.nan)

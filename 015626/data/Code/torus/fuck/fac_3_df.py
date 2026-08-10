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


def ema_span_1(factor_array, d, span):
    return ema_1(factor_array, d=d, alpha=2 / (span + 1))


def calculate_exceeding_length(c, h, l, window):
    hl = h - l
    non_covered_up = np.maximum(c[1:] - h[:-1], 0) / replace_zero(hl[1:])
    non_covered_down = np.maximum(l[:-1] - c[1:], 0) / replace_zero(hl[1:])
    avg_gain = ema_span_1(non_covered_up[-(window * 3):], window * 3, window)
    avg_loss = ema_span_1(non_covered_down[-(window * 3):], window * 3, window)
    exceeding_length_rsi = avg_gain / replace_zero(avg_gain + avg_loss) * 100
    return exceeding_length_rsi


class fac_3_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 1 * self.freq
        self.required_columns = ['close', 'high', 'low']
        self.normalize_size = 3 * self.bars
        self.normalize_type = 'ts_rank'

        self.exceeding_length_rsi_list = []
        self.exceeding_length_rsi_ema_list = []

    def calculate(self, data):
        c = data['close']
        h = data['high']
        l = data['low']

        aaa = 7
        bbb = 7
        ccc = 2

        exceeding_length_rsi = calculate_exceeding_length(c, h, l, bbb)
        self.exceeding_length_rsi_list.append(exceeding_length_rsi)
        exceeding_length_rsi_ema = ema_span_1(np.array(self.exceeding_length_rsi_list[-(aaa * 3):]), aaa * 3, aaa)
        self.exceeding_length_rsi_ema_list.append(exceeding_length_rsi_ema)
        sig = nanmean_np(np.array(self.exceeding_length_rsi_ema_list[-ccc:]))
        return sig

    def pre_calculate(self, data):
        c_all = data['close']
        h_all = data['high']
        l_all = data['low']

        aaa = 7
        bbb = 7

        n = 30
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

            exceeding_length_rsi = calculate_exceeding_length(c, h, l, bbb)
            self.exceeding_length_rsi_list.append(exceeding_length_rsi)
            if len(self.exceeding_length_rsi_list) >= aaa * 3:
                exceeding_length_rsi_ema = ema_span_1(np.array(self.exceeding_length_rsi_list[-(aaa * 3):]), aaa * 3, aaa)
                self.exceeding_length_rsi_ema_list.append(exceeding_length_rsi_ema)

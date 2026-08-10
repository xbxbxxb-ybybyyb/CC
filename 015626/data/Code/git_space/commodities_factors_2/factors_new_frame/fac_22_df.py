from rolling_adj import *
from operators_cc_com import *
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


class fac_22_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 3 * self.freq
        self.required_columns = ['close']
        self.normalize_size = 1
        self.normalize_type = 'ts_rank'

        self.dpo_raw_list = []
        self.dpo_ma_raw_list = []

    def calculate(self, data):
        c = data['close']

        coef = int(self.bars / self.freq)
        aaa = max(coef, 150)
        bbb = 12
        ccc = 5

        sss = int(aaa / 2 + 1)
        dpo_raw = c[-1] - nanmean_np(c[-aaa - sss:-sss])
        self.dpo_raw_list.append(dpo_raw)

        c_diff = c[1:] - c[:-1]
        co = nanstd_np(c_diff[-60:], ddof=1)
        dpo_ma_raw = ema_1(np.array(self.dpo_raw_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        dpo_ma_raw = dpo_ma_raw / replace_zero(co)
        self.dpo_ma_raw_list.append(dpo_ma_raw)

        sig = rank_data(np.array(self.dpo_ma_raw_list[-ccc:]))
        return sig

    def pre_calculate(self, data):
        self.dpo_raw_list = []
        self.dpo_ma_raw_list = []
        c_all = data['close']

        coef = int(self.bars / self.freq)
        aaa = max(coef, 150)
        bbb = 12
        ccc = 5

        n = aaa * 2 + bbb * 3 + ccc
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
            else:
                c = c_all[:-j]

            sss = int(aaa / 2 + 1)
            if len(c) > 1:
                dpo_raw = c[-1] - nanmean_np(c[-aaa - sss:-sss])
            else:
                dpo_raw = np.nan
            self.dpo_raw_list.append(dpo_raw)

            if len(self.dpo_raw_list) >= bbb * 3:
                c_diff = c[1:] - c[:-1]
                co = nanstd_np(c_diff[-60:], ddof=1)
                dpo_ma_raw = ema_1(np.array(self.dpo_raw_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
                dpo_ma_raw = dpo_ma_raw / replace_zero(co)
            else:
                dpo_ma_raw = np.nan
            self.dpo_ma_raw_list.append(dpo_ma_raw)


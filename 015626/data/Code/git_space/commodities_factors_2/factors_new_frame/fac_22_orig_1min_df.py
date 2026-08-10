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


class fac_22_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 2 * self.freq
        self.required_columns = ['close', 'dt']
        self.normalize_size = 1
        self.normalize_type = 'ts_rank'

        self.dpo_raw_list = []
        self.dpo_ma_raw_list = []

    def calculate(self, data):
        c = data['close']
        t = data['dt']

        aaa = 120
        bbb = 20
        ccc = 25

        minute_drop_now = t[:-1].astype('datetime64[m]').astype('int64') % 60
        close_drop_now = c[:-1]
        close = close_drop_now[minute_drop_now % 3 == 2]

        if len(close) > 0:
            sss = int(aaa / 2 + 1)
            dpo_raw = close[-1] - nanmean_np(close[-aaa - sss:-sss])
        else:
            dpo_raw = np.nan
        minute_now = t[-1].astype('datetime64[m]').astype('int64') % 60
        if minute_now % 3 == 0:
            self.dpo_raw_list.append(dpo_raw)

        dpo_ma_raw = ema_1(np.array(self.dpo_raw_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
        self.dpo_ma_raw_list.append(dpo_ma_raw)

        sig = rank_data(np.array(self.dpo_ma_raw_list[-ccc:]))
        return sig

    def pre_calculate(self, data):
        self.dpo_raw_list = []
        self.dpo_ma_raw_list = []
        c_all = data['close']
        t_all = data['dt']

        aaa = 120
        bbb = 20
        ccc = 25

        n = aaa * 2 + bbb * 9 + ccc
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                t = t_all
            else:
                c = c_all[:-j]
                t = t_all[:-j]

            if (len(c) >= 3) and (len(c) == len(t)):
                minute_drop_now = t[:-1].astype('datetime64[m]').astype('int64') % 60
                close_drop_now = c[:-1]
                close = close_drop_now[minute_drop_now % 3 == 2]
                if len(close) > 0:
                    sss = int(aaa / 2 + 1)
                    dpo_raw = close[-1] - nanmean_np(close[-aaa - sss:-sss])
                    minute_now = t[-1].astype('datetime64[m]').astype('int64') % 60
                    if minute_now % 3 == 0:
                        self.dpo_raw_list.append(dpo_raw)
            else:
                pass

            if len(self.dpo_raw_list) >= bbb * 3:
                dpo_ma_raw = ema_1(np.array(self.dpo_raw_list[-(bbb * 3):]), bbb * 3, 1 / (bbb + 1))
            else:
                dpo_ma_raw = np.nan
            self.dpo_ma_raw_list.append(dpo_ma_raw)

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


class fac_17_orig_1min_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 20 * self.freq 
        self.required_columns = ['close', 'tday']
        self.normalize_size = 300
        self.normalize_type = 'ts_rank'

        self.sig_list = []

    def calculate(self, data):
        c = data['close']
        t = data['tday']

        aaa = 230
        bbb = 30

        ut = np.unique(t)
        if len(ut) >= int(np.sqrt(aaa)) + 1:
            tday_new = ut[-int(np.sqrt(aaa)) - 1]
            open_price = c[t == tday_new][0]
            length = len(t) - np.argmax(t == tday_new) - 1
            sig = (c[-1] - open_price) / length
            self.sig_list.append(sig)
        elif len(ut) > 0:
            tday_new = ut[0]
            open_price = c[t == tday_new][0]
            length = len(t) - np.argmax(t == tday_new) - 1
            sig = (c[-1] - open_price) / length
            self.sig_list.append(sig)
        else:
            self.sig_list.append(np.nan)

        
        sig = ema_1(np.array(self.sig_list[-bbb:]), bbb, 1 / 5)

        return sig

    def pre_calculate(self, data):
        c_all = data['close']
        t_all = data['tday']

        aaa = 230
        bbb = 30

        n = bbb
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                t = t_all
            else:
                c = c_all[:-j]
                t = t_all[:-j]
            ut = np.unique(t)
            if len(ut) >= int(np.sqrt(aaa)) + 1:
                tday_new = ut[-int(np.sqrt(aaa)) - 1]
            elif len(ut) > 0:
                tday_new = ut[0]
            else:
                self.sig_list.append(np.nan)
                continue
            open_price = c[t == tday_new][0]
            length = len(t) - np.argmax(t == tday_new)
            try:
                sig = (c[-1] - open_price) / length
                self.sig_list.append(sig)
            except:
                self.sig_list.append(np.nan)

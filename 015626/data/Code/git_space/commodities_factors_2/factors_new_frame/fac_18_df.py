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


class fac_18_df(FutureFactor):
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.bars = self.bars_dict[self.ticker]
        self.tick = self.tick_size_dict[self.ticker]

        self.days_past = 5 * self.freq
        self.required_columns = ['close', 'volume']
        self.normalize_size = 1
        self.normalize_type = 'ts_rank'

        self.sig_list = []
        self.sig2_list = []
        self.sig3_list = []

    def calculate(self, data):
        c = data['close']
        v = data['volume']

        aaa = int(12 / self.freq)
        bbb = max([max([int(9 / self.freq), 3]), self.freq])
        ccc = 3

        minute_ret = c[1:] - c[:-1]
        vol = nanstd_np(minute_ret[-60:], ddof=1)
        amihund_measure_raw = minute_ret[-1] / replace_zero(v[-1] * vol)
        self.sig_list.append(amihund_measure_raw)

        amihund_measure_raw_ma = nanmean_np(np.array(self.sig_list[-aaa:]))
        self.sig2_list.append(amihund_measure_raw_ma)

        amihund_measure_raw_ma = nanmean_np(np.array(self.sig2_list[-bbb:]))
        self.sig3_list.append(amihund_measure_raw_ma)

        sig = rank_data(np.array(self.sig3_list[-(ccc * 300):]))
        return sig

    def pre_calculate(self, data):
        self.sig_list = []
        self.sig2_list = []
        self.sig3_list = []

        c_all = data['close']
        v_all = data['volume']

        aaa = int(12 / self.freq)
        bbb = max([max([int(9 / self.freq), 3]), self.freq])
        ccc = 3

        n = aaa + bbb + ccc * 300
        for i in range(n):
            j = n - 1 - i
            if j == 0:
                c = c_all
                v = v_all
            else:
                c = c_all[:-j]
                v = v_all[:-j]
            if  (len(c) > 1) and (len(v) > 1):
                
                minute_ret = c[1:] - c[:-1]
                vol = nanstd_np(minute_ret[-60:], ddof=1)
                amihund_measure_raw = minute_ret[-1] / replace_zero(v[-1] * vol)
                self.sig_list.append(amihund_measure_raw)
            else:
                self.sig_list.append(np.nan)

            if len(self.sig_list) >= aaa:
                amihund_measure_raw_ma = nanmean_np(np.array(self.sig_list[-aaa:]))
                self.sig2_list.append(amihund_measure_raw_ma)

            if len(self.sig2_list) >= bbb:
                amihund_measure_raw_ma = nanmean_np(np.array(self.sig2_list[-bbb:]))
                self.sig3_list.append(amihund_measure_raw_ma)

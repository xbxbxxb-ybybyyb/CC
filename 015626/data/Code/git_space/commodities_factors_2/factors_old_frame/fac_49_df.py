import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from operators_wsc_1_0 import *

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))




# wsc8_future_if
class fac_49_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'low', 'second_main_mask']

        super(fac_49_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, a = 30, b = 80, c = 60, d = 4):
        a = 180
        b = 60
        c = 5
        d = 1
        mask = data['second_main_mask']
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        close = data['close'][mask].mean(axis = 1)
        high = data['high']
        low = data['low']
        low_n = ts_min(low, a)[mask].mean(axis = 1)
        high_n = ts_max(high, a)[mask].mean(axis = 1)
        temp1 = high_n - low_n
        temp1[abs(temp1)<1e-8] = np.nan
        temp2 = (close- low_n) / r(high_n - low_n)
        b_low = ts_min(temp2, b)
        b_high = ts_max(temp2, b)
        temp3 = b_high - b_low
        temp3[abs(temp3)<1e-8] = np.nan
        temp4 = (temp2 - b_low) / r(temp3)
        factor = temp4.copy()
        factor = factor + ts_truncated_ema_span_1(temp4, c*3, c)
        factor = ts_rank(factor,  d * 200)
        factor.name = self.__class__.__name__
        return factor.to_frame()
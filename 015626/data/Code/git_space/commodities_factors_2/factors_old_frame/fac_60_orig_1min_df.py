import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import ts_rank, r
from utils_zsj import *
from operators_wsc_1_0 import *
from help_functions_wsc import *
# wsc_spot_38_if

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


class fac_60_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'second_main_mask']

        super(fac_60_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc, ddd):
        aaa = 15
        bbb = 60
        ccc = 25
        ddd = 10
        spot_close_if = data['close']
        mask = data['second_main_mask']
        factor_raw = (np.sign(spot_close_if.diff(aaa)) * ts_sum((spot_close_if.diff(aaa) ** 2), bbb))[mask].mean(axis = 1)
        factor = ts_truncated_ema_1(factor_raw, ccc * 3, 1/(ccc+1))
        factor = ts_rank(factor, 300 * ddd)
        factor.name = self.__class__.__name__
        return factor.to_frame()


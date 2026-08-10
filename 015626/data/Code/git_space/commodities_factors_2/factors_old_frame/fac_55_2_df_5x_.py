import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# ERET_CC_IF

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))


class fac_55_2_df_5x_(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'low', 'main_mask']

        super(fac_55_2_df_5x_, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bbb, ccc):

        mask = data['main_mask']
        hlow = (data['low'].rolling(aa, min_periods = int(aa/2)).min())[mask].mean(axis = 1) 
        hclose = data['close'][mask].mean(axis = 1)
        lltc_ind_r = (-(hlow- (hclose)) )
        factor = ts_truncated_ema_1(lltc_ind_r, bbb * 3, 1/(bbb + 1)).to_frame()

        factor.columns = [self.__class__.__name__]
        factor = ts_rank(factor, ccc)

        return factor

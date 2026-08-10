import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

    

#CDO_ind
class fac_61_aug_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open', 'second_main_mask']

        super(fac_61_aug_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):

        aa = 10
        bb = 30
        ccc = 20
        
        mask = data['second_main_mask']

        cdo_r = data['close'].rolling(aa, min_periods = 1).mean()-data['open'].rolling(aa, min_periods = 1).mean()

        factor = cdo_r[mask].mean(axis = 1).to_frame()
        
        factor.columns = [self.__class__.__name__]
        
        factor = ts_truncated_ema_1(factor, bb * 3, 1/(bb + 1))# + ts_truncated_ema_1(factor, 10 * 3, 1/(10 + 1))
        
        factor = ts_rank(factor, ccc * 300)

        return factor
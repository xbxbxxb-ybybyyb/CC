import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# HLDL2_ind_CC_IF
def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

# OCtHL
class fac_34_aug_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open', 'high', 'low', 'main_mask']

        super(fac_34_aug_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb):

        mask = data['main_mask']
        #second_mask = data['second_main_mask']
        #weight = data['amount'].div(data['amount'].sum(axis = 1), axis = 0)
        aa = 20

        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        
        temp1 = data['open'].rolling(2, min_periods = 1).mean() - data['close']#.rolling(5, min_periods = 1).mean()
        temp2 = data['high'].rolling(2, min_periods = 1).max()  - data['low'].rolling(2, min_periods = 1).min() 
        t_pcor2 = (-temp1/r(temp2))[mask].mean(axis = 1)
        t_pcor2[t_pcor2 == np.inf] = 0
        fac = ts_truncated_ema_span_1(t_pcor2.rolling(10, min_periods = 1).mean(), 100, 45)

        
        factor = ts_rank(fac, 600).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor
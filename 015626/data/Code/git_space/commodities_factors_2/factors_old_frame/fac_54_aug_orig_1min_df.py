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


# 

class fac_54_aug_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'open', 'high', 'low','main_mask']

        super(fac_54_aug_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data, aaa = 5, bbb = 45, ccc = 8, ddd = 5):
        mask = data['main_mask']
        twap = (data['close'] + data['open'] + data['high'] + data['low']) / 4
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        price_level = rolling_norm(twap,  240)
        price_std = (twap.pct_change()).rolling(60, min_periods = 5).std()
        factor = (price_level / r(price_std))[mask].mean(axis = 1)
        factor = ts_rank(factor.rolling(8, min_periods = 1).mean(), coef * 5).to_frame()
        factor.columns = [self.__class__.__name__]
        return factor
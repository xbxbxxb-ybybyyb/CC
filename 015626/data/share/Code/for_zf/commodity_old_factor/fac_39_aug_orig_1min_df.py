import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from operators_all_wsc import cross_hub_num

# sr1_zf
def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))



class fac_39_aug_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'high', 'second_main_mask']

        super(fac_39_aug_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        aa = 35
        bb = 5
        ccc = 5
        mask = data['second_main_mask']
        rtn = (data['close'] - data['close'].shift(1))[mask].mean(axis = 1) 
        vol = rtn.rolling(aa, min_periods=1).std()
        co = cross_hub_num(data['close'], 60)[mask].mean(axis = 1) + 1
        ret = (data['close'] - (data['high'].shift(1).rolling(aa, min_periods=1).max()))[mask].mean(axis = 1)

        sig = ts_truncated_ema_1(ret / r(vol) / r(np.sqrt(co)), bb*3, 1/(bb+1))
        sig = ts_rank(sig, 300 * ccc)

        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)

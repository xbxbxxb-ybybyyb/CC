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



class fac_57_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'low', 'second_main_mask']

        super(fac_57_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        aa = 240
        bb = 10
        ccc = 5
        mask = data['second_main_mask']
        rtn = (data['close'] - data['close'].shift(1))[mask].mean(axis = 1) 
        vol1 = rtn.rolling(90, min_periods=1).std()
        vol2 = rtn.rolling(360, min_periods=1).std()
        co = cross_hub_num(data['close'], 30)[mask].mean(axis = 1) + 1
        ret1 = (data['close'] - (data['low'].shift(1).rolling(90, min_periods=1).min()))[mask].mean(axis = 1)
        ret2 = (data['close'] - (data['low'].shift(1).rolling(360, min_periods=1).min()))[mask].mean(axis = 1)
        
        temp = ret1 / r(vol1) / r(np.sqrt(co)) + 2 * ret2 / r(vol2) / r(np.sqrt(co))
        sig = ts_truncated_ema_1(temp, bb*3, 1/(bb+1))
        sig = ts_rank(sig, 300 * ccc)

        sig.name = self.__class__.__name__
        return pd.DataFrame(sig)
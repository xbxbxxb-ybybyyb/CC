import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from operators_all_wsc import cross_hub_num

# LMLS
def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))



class fac_56_aug_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=[ 'low', 'high', 'main_mask', 'close']

        super(fac_56_aug_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        
    def on_bar(self, data, aa, bb, ccc):
        aa = 15
        bb = 120
        ccc = 3
        ddd = 1200

        if bb < 100:
            bb_temp = np.nanmax([int(aa * bb / 100), 1])
        elif (bb >= 100) and (bb < 200):
            bb_temp = int(aa / 3)
        else:
            bb_temp = int(aa * 2 / 3)
        
        mask = data['main_mask']
        temp1 = data['low'].rolling(aa, min_periods = 1).mean() - data['low'].shift(bb_temp).rolling(aa - bb_temp, min_periods = 1).min()
        temp2 = data['high'].rolling(aa, min_periods = 1).mean() - data['high'].shift(bb_temp).rolling(aa - bb_temp, min_periods = 1).max()
        temp = temp1 + temp2
        temp = temp[mask].mean(axis = 1)
        co = (data['close'].rolling(30, min_periods = 1).std())[mask].mean(axis = 1)
        co2 = (cross_hub_num(data['close'], aa) + 1)[mask].mean(axis = 1)
        #temp = temp + 1.5 * temp.rolling(10, min_periods = 1).mean()
        factor = (temp * r(co) / r(co2)).to_frame()
        factor = factor + 1.2 * factor.rolling(10, min_periods = 1).mean()
        factor.columns = [self.__class__.__name__]
    
        factor = ts_rank(factor, ddd)

        return factor

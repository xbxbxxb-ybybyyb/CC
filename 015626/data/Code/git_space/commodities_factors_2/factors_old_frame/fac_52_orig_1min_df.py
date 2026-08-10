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

class fac_52_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'twap', 'main_mask']

        super(fac_52_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        aaa = 10
        bbb = 30
        ccc = 30
        
        
        
        mask = data['main_mask'].copy()
        #coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        fac = (- data['twap'].rolling(2, min_periods = 1).mean().rolling(aaa, min_periods = 1).mean() / data['close'].rolling(2, min_periods = 1).mean().rolling(aaa, min_periods = 1).mean()) 
        fac = fac[mask].mean(axis = 1).to_frame()
        factor = ts_rank(ts_truncated_ema_1(fac, bbb * 3, 1 / (bbb + 1)), ccc * 300)
        factor.columns = [self.__class__.__name__]      
        return factor
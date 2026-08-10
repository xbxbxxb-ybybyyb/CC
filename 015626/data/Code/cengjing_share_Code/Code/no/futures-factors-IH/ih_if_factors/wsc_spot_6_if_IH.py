import numpy as np
import pandas as pd
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_spot_6_if_IH(FutureFactor):
    """
    sum((x_0 + x_(-i) - x_(-i//2) / 2 * x_(-i//2)) for i in range(2, 24, 2)
    """
    data_type = 'Future'
    days_past = 1
    data_dict = dict()
    data_dict['Index_Id'] = {'000016.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        spot_close = data['close_000016.SH'].iloc[-40:]
        n = 24
        factor_init = pd.DataFrame(index=spot_close.index, columns=np.arange(2, n, 2))
        for i in range(2, n, 2):
            factor_init[i] = (spot_close + ts_delay(spot_close, i) - 2 * ts_delay(spot_close, i//2)) / ts_delay(spot_close, i//2)
        factor_raw = -factor_init.mean(axis=1)
        factor = ts_mean(factor_raw, 10)
        return factor.iloc[-1]

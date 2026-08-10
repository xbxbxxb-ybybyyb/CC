import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_ti9_cfg_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'open', 'low', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-60:]
        stk_open = data['open_preadj'].values[-60:]
        stk_low = data['low_preadj'].values[-60:]
        stk_weight = data['weight'].values[-60:]
        x = stk_close - stk_open
        y = stk_open.copy()
        y = np.where(x<0, stk_close, y)
        z = replace_zero(y - stk_low)
        u = x / z
        factor_init = np.nansum(u * stk_weight, axis=1)
        factor_raw = ts_mean(factor_init, 60)
        return factor_raw[-1]


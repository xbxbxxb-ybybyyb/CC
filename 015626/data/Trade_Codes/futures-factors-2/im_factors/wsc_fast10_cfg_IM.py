import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_fast10_cfg_IM(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['open', 'close', 'high', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_open = data['open_preadj'].values[-30:]
        stk_close = data['close_preadj'].values[-30:]
        stk_high = data['high_preadj'].values[-30:]
        stk_weight = data['weight'].values[-30:]

        x = stk_close - stk_open
        y = np.where(x>0, stk_close, stk_open)
        z = replace_zero(stk_high - y)
        u = x / z
        factor_raw = np.nansum(u * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 30)       
        return factor_mean[-1]
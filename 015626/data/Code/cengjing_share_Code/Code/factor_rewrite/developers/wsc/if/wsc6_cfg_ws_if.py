import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc6_cfg_ws_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'close']
    normalize_size = 480
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-65:]
        stk_close = data['close_preadj'].values[-65:]
        stk_ret_short = ts_pct_change(stk_close, 10)
        stk_ret_long = ts_pct_change(stk_close, 60)
        factor_init = stk_ret_long - stk_ret_short
        factor_init[factor_init<0] = 0
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        return factor_mean[-1]

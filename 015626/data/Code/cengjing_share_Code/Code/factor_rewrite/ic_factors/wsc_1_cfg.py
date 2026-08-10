import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_1_cfg(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-45:]
        stk_weight = data['weight'].values[-45:]
        stk_amount = data['amount'].values[-45:]
        stk_ret = ts_pct_change(stk_close, 1)
        log_ret = log(stk_ret + 1)
        ret_std = ts_std(stk_ret, 15)
        log_ret_weight = log_ret * stk_amount * ret_std
        factor_raw = np.nansum(ts_sum(log_ret_weight, 30)*stk_weight, axis=1)
        return factor_raw[-1]
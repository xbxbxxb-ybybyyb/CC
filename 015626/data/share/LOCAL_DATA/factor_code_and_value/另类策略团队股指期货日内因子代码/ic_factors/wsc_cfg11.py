import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_cfg11(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-25:]
        stk_weight = data['weight'].values[-25:]
        stk_ret = ts_pct_change(stk_close, 5)
        ret_mean = ts_mean(stk_ret, 20)
        ret_std = ts_std(stk_ret, 20)
        factor_init = ret_mean + ret_std
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        return factor_raw[-1]
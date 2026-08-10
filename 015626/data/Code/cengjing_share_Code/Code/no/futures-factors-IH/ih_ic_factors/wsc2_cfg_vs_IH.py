import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc2_cfg_vs_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-48:]
        stk_volatility_mask = data['stk_volatility'].values[-48:]
        stk_ret = ts_pct_change(stk_close, 3)
        ret_mean = ts_mean(stk_ret, 30)
        factor_init = np.nansum(ret_mean * stk_volatility_mask, axis=1)
        factor_raw = ts_mean(factor_init, 15)
        return factor_raw[-1]

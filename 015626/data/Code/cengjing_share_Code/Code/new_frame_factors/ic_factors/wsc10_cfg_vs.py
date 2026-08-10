import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc10_cfg_vs(FutureFactor):
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
        stk_close = data['close_preadj'].values[-131:]
        # print(stk_close.shape)
        stk_volatility = data['stk_volatility'].values[-131:]
        stk_ret_long = ts_pct_change(stk_close, 130)
        stk_ret_short = ts_pct_change(stk_close, 10)
        factor_init = stk_ret_long - stk_ret_short
        factor_init[factor_init < 0] = 0
        factor_raw = np.nansum(factor_init[-1] * stk_volatility[-1])
        return factor_raw

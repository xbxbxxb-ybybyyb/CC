import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero, replace_inf



class wsc9_cfg_ws_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Stock'] = ['weight', 'close']
    normalize_size = 480
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-189:]
        stk_close = data['close_preadj'].values[-189:]
        spot_close = data['close_000300.SH'].values[-189:]
        spot_ret = ts_pct_change(spot_close, 3)
        stk_ret = ts_pct_change(stk_close, 3)
        ret_diff = stk_ret - spot_ret
        ret_diff_bool = (ret_diff > 0) + 0.0
        ret_diff_bool[np.isnan(ret_diff)] = np.nan
        temp = ts_sum(ret_diff_bool, 120)
        factor_init = replace_inf(ts_sum(ret_diff_bool, 20) / replace_zero(temp))
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_mean = -ts_mean(factor_raw, 45)
        return factor_mean[-1]

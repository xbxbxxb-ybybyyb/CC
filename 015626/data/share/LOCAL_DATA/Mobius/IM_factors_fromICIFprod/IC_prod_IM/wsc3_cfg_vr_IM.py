import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero, replace_inf



class wsc3_cfg_vr_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000852.SH':['close']}
    data_dict['Stock'] = ['close', 'stk_volatility', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].iloc[-118:]
        stk_volatility = data['stk_volatility'].values[-118:]
        spot_close = data['close_000852.SH'].iloc[-118:]
        stk_volatility_rank_mask = 2 * section_rank_np(stk_volatility, pct=True) - 1
        spot_ret = ts_pct_change(spot_close, 3)
        stk_ret = ts_pct_change(stk_close, 3)
        ret_diff = stk_ret.sub(spot_ret.iloc[:,0], axis=0)
        ret_diff[ret_diff > 0] = 1
        ret_diff[ret_diff <= 0] = 0
        ret_diff = ret_diff.values
        temp = replace_zero(ts_sum(ret_diff, 90))
        factor_init = replace_inf(ts_sum(ret_diff, 15) / temp)
        factor_raw = np.nansum(factor_init * stk_volatility_rank_mask, axis=1)
        factor_mean = ts_mean(factor_raw, 25)
        return factor_mean[-1]

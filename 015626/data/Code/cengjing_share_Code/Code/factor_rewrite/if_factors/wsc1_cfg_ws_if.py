import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc1_cfg_ws_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Index_Id'] = {'000300.SH':['close']}
    data_dict['Stock'] = ['weight', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-71:]
        stk_close = data['close_preadj'].values[-71:]
        spot_close = data['close_000300.SH'].values[-71:]
        stk_ret = ts_pct_change(stk_close, 60)
        spot_ret = ts_pct_change(spot_close, 60)
        excess_ret = stk_ret - spot_ret
        stk_weight[np.isnan(excess_ret)] = np.nan
        stk_weight[excess_ret >= 0] = np.nan
        factor_raw = np.nansum(stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        return factor_mean[-1]

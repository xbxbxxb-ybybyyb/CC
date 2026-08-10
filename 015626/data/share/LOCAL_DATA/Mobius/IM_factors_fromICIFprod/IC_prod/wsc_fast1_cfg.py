import numpy as np
from operators_wsc_1_0 import *
from future_factor import FutureFactor


class wsc_fast1_cfg(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'weight', 'adjfactor']
    data_dict['Index_Id'] = {'000905.SH':['close']}
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        spot_close = data['close_000905.SH'].values[-24:]
        stk_close = data['close_preadj'].values[-24:]
        stk_weight = data['weight'].values[-24:]

        spot_ret = ts_pct_change(spot_close, 20)
        stk_ret = ts_pct_change(stk_close, 20)
        excess_ret = sub2(stk_ret, spot_ret)
        stk_weight[excess_ret >= 0] = np.nan
        factor_raw = np.nansum(stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 3)
        return factor_mean[-1]
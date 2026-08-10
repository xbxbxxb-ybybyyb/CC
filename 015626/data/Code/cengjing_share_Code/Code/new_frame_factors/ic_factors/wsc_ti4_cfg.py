import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_ti4_cfg(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-37:]
        stk_amount = data['amount'].values[-37:]
        price_diff = ts_delta(stk_close, 1)
        up_num = np.nansum((price_diff>=0), axis=1)
        down_num = np.nansum((price_diff<0), axis=1)
        up_amount = stk_amount.copy()
        up_amount[price_diff<0] = 0
        up_amount = np.nansum(up_amount, axis=1)
        down_amount = stk_amount.copy()
        down_amount[price_diff>=0] = 0
        down_amount = np.nansum(down_amount, axis=1)
        factor_init = (up_num / replace_zero(down_num+0.)) / replace_zero(up_amount / replace_zero(down_amount))
        factor_raw = -ts_mean(factor_init, 35)
        return factor_raw[-1]

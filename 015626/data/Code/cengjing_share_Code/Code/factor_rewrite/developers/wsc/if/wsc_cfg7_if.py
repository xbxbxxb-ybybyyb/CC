import numpy as np
import numpy.mask as ma
from future_factor import FutureFactor
from operators_wsc_1_0 import *




class wsc_cfg7_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-24:]
        stk_weight = data['weight'].values[-24:]
        stk_amount = data['amount'].values[-24:]
        stk_ret = ts_pct_change(stk_close, 3)
        stk_ret_mask = np.nanquantile(stk_ret, 0.8, axis=1, keepdims=True)
        amount_after_mask = ma.array(stk_amount, mask=(stk_ret<=stk_ret_mask))
        factor_raw = np.nansum(amount_after_mask*stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]

import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_cfg5(FutureFactor):
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
        stk_close = data['close_preadj'].values[-23:]
        stk_amount = data['amount'].values[-23:]
        stk_weight = data['weight'].values[-23:]
        stk_ret = ts_pct_change(stk_close, 3)
        stk_ret_mask = np.nanquantile(stk_ret, 0.9, axis=1)
        stk_ret_mask = np.expand_dims(stk_ret_mask, axis=-1)
        amount_after_mask = ma.array(stk_amount, mask=(stk_ret<=stk_ret_mask))
        factor_raw = np.nansum(amount_after_mask * stk_weight, axis=1)
        factor_raw = ts_mean(factor_raw, 20)
        return factor_raw[-1]

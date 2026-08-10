import numpy as np
import numpy.ma as ma
from future_factor import FutureFactor
from operators_wsc_1_0 import *

class wsc20_cfg_ar_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'rolling_norm'
#    num_range = '(0,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-87:]
        stk_close = data['close_preadj'][-87:]
        stk_ret = ts_pct_change(stk_close.values, 1)
        stk_skew = stk_close.rolling(30, min_periods = 15).skew().values
        stk_skew_mask = np.nanquantile(stk_skew, 0.5, axis=1, keepdims=True)
        factor_init = ma.array(stk_ret, mask=(stk_skew<=stk_skew_mask))
        factor_raw = np.nansum(factor_init * stk_amount, axis=1) / np.nansum(stk_amount * (stk_skew>stk_skew_mask), axis=1)
        factor_mean = ts_mean(factor_raw, 55)
        return factor_mean[-1]
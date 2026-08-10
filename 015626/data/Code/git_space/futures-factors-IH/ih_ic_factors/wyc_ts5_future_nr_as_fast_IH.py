import numpy as np
from operators_wsc_1_0 import *
from future_factor import FutureFactor



class wyc_ts5_future_nr_as_fast_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'adjfactor']
    normalize_size = 237 * 5
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_close = data['close_preadj'].values[-91:]
        stk_amount = data['amount'].values[-91:]
        
        N = 45
        temp1 = ts_delta(ts_sum(stk_close, N) / N, N) / ts_delay(stk_close, N)
        temp2 = stk_close - ts_min(stk_close, N)
        temp3 = ts_delta(stk_close, 3)
        factor_raw = np.where(temp1<=0.05, temp2, temp3)
        factor_raw = np.nansum(factor_raw * stk_amount, axis=1)
        return factor_raw[-1]
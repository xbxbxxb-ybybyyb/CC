import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc22_cfg_search_as_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'open', 'adjfactor']
    normalize_size = 2400
    normalize_type = 'ts_rank'
    num_range = '(0,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-56:]
        stk_open = data['open_preadj'].values[-56:]
        factor_init = ts_median(ts_delta(stk_open, 25), 25)
        factor_raw = np.nansum(factor_init * stk_amount, axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        return factor_mean[-1]

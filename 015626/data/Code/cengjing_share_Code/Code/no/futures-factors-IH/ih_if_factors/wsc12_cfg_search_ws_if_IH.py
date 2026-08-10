import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc12_cfg_search_ws_if_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'close', 'adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-85:]
        stk_close = data['close_preadj'].values[-85:]
        factor_init = ts_reg_beta(stk_close, 40)
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        return factor_mean[-1]

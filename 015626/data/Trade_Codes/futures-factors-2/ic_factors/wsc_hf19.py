import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


    
class wsc_hf19(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['amount', 'PxStd', 'VolStd']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_amount = data['amount'].values[-15:]
        stk_PxStd = data['PxStd'].values[-15:]
        stk_VolStd = data['VolStd'].values[-15:]
        factor_init = pairwise_corr_np(ts_mean(stk_PxStd, 15)[-1], ts_mean(stk_VolStd, 15)[-1])
        factor_raw = -factor_init * ts_mean(np.nansum(stk_amount, axis=1), 15)[-1]
        return factor_raw
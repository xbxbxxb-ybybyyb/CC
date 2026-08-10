import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


    
class wsc_hf15_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'PxVolCorr']
    normalize_size = 1800
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-20:]
        stk_PxVolCorr = data['PxVolCorr'].values[-20:]
        factor_init = np.nansum(stk_weight*stk_PxVolCorr, axis=1)
        factor_raw = ts_mean(factor_init, 20)
        return factor_raw[-1]
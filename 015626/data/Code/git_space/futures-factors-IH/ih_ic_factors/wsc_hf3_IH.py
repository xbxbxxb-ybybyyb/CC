import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class wsc_hf3_IH(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['Ask1AmtMean']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_Ask1AmtMean = data['Ask1AmtMean'].values[-75:]
        a = np.nansum(stk_Ask1AmtMean, axis=1)
        factor_init = ts_rank(a, 30)
        factor_raw = -ts_mean(factor_init, 45)
        return factor_raw[-1]
import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class pp_abs_to_c_w_ic(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['AbsPxPath', 'close', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        AbsPxPath = data['AbsPxPath'].values[-1]
        close = data['close'].values[-1]
        weight = data['weight'].values[-1]

        factor = np.nansum(AbsPxPath / replace_zero(close) * weight)
        if factor > 0.05:
            factor = np.nan
        return factor
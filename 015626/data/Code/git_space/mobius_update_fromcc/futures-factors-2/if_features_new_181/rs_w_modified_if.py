import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class rs_w_modified_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['stk_volatility', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_volatility = data['stk_volatility'].values[-1]
        weight = data['weight'].values[-1]

        factor = np.nansum(stk_volatility * weight)
        if factor > 0.02:
            factor = np.nan
        return np.log(factor) if factor > 0 else np.nan
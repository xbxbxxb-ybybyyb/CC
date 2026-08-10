import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class boba_2_ic(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_big_lo_amount']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_big_lo_amount = data['buy_big_lo_amount'].values[-1]

        factor = np.nansum(buy_big_lo_amount)
        return np.log(factor) if factor > 0 else np.nan
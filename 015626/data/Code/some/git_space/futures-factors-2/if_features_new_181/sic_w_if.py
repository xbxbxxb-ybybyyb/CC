import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class sic_w_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['stk_index_corr_hs300', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_index_corr_hs300 = data['stk_index_corr_hs300'].values[-1]
        weight = data['weight'].values[-1]

        factor = np.nansum(stk_index_corr_hs300 * weight)
        return factor
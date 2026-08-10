import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class sba_1_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_superorder_money_v2']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_superorder_money_v2 = data['sell_superorder_money_v2'].values[-1]

        factor = np.nansum(sell_superorder_money_v2)
        return np.log(factor) if factor > 0 else np.nan
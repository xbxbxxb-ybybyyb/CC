import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class oa_to_on_im(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['lo_amount', 'lo_counts']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        lo_amount = data['lo_amount'].values[-1]
        lo_counts = data['lo_counts'].values[-1]

        factor = np.nansum(lo_amount) / np.nansum(lo_counts)
        return factor
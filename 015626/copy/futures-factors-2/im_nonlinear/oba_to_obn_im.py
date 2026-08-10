import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class oba_to_obn_im(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_lo_amount', 'buy_lo_counts']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_lo_amount = data['buy_lo_amount'].values[-1]
        buy_lo_counts = data['buy_lo_counts'].values[-1]

        factor = np.nansum(buy_lo_amount) / np.nansum(buy_lo_counts)
        return factor
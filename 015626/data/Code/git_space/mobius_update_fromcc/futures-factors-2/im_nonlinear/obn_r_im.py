import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class obn_r_im(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_lo_counts', 'sell_lo_counts']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_lo_counts = data['buy_lo_counts'].values[-1]
        sell_lo_counts = data['sell_lo_counts'].values[-1]

        factor = np.nansum(buy_lo_counts) / np.nansum(buy_lo_counts + sell_lo_counts)
        return factor
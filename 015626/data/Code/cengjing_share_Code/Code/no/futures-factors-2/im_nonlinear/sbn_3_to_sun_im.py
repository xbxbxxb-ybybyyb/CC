import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class sbn_3_to_sun_im(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_midorder_count_v2', 'SellUniqueOrderNum']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_midorder_count_v2 = data['sell_midorder_count_v2'].values[-1]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-1]

        factor = np.nansum(sell_midorder_count_v2) / np.nansum(SellUniqueOrderNum)
        return factor
import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class bbn_2_to_bun_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_count', 'BuyUniqueOrderNum']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_bigorder_count = data['buy_bigorder_count'].values[-1]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-1]

        factor = np.nansum(buy_bigorder_count) / np.nansum(BuyUniqueOrderNum)
        return factor
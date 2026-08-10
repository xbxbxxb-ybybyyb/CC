import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


    
class wsc_hf_10_srch_if(FutureFactor):

    """
    ts_argmin(bun_r, 15) - ts_argmax(bun_r, 15)
    """
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_unique_num = data['BuyUniqueOrderNum'].values[-15:]
        sell_unique_num = data['SellUniqueOrderNum'].values[-15:]
        
        bun = np.nansum(buy_unique_num, axis=1)
        sun = np.nansum(sell_unique_num, axis=1)
        
        bun_r = bun / (bun + sun)
        factor = ts_argmin(bun_r, 15) - ts_argmax(bun_r, 15)
        return factor[-1]
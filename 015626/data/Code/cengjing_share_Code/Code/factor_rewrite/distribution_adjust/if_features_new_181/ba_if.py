import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class ba_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeMoney = data['BuyTradeMoney'].values[-1]

        factor = np.nansum(BuyTradeMoney)
        return np.log(factor) if factor > 0 else np.nan
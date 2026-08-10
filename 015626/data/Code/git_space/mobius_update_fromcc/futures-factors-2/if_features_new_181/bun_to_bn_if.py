import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class bun_to_bn_if(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-1]
        BuyTradeNum = data['BuyTradeNum'].values[-1]

        factor = np.nansum(BuyUniqueOrderNum) / np.nansum(BuyTradeNum)
        return factor
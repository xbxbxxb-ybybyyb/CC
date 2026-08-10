import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor



class wyc_bigon_cfghf_fast_IH(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeNum', 'BuyUniqueOrderNum']
    normalize_size = 237 * 3
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_BuyTradeNum = data['BuyTradeNum'].values[-1]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-1]
        
        btn = replace_zero(stk_BuyTradeNum)
        factor_raw = 1 - stk_BuyUniqueOrderNum / btn
        factor_raw = np.nansum(factor_raw)
        return factor_raw
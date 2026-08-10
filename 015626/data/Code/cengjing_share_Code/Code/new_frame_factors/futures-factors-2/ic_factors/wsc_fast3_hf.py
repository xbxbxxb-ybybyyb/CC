import numpy as np
from operators_wsc_1_0 import *
from help_functions_wsc import *
from future_factor import FutureFactor


class wsc_fast3_hf(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum', 'BuyTradeNum', 'weight']
    normalize_size = 1200 
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False

    def calculate(self, data):
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-4:]
        stk_BuyTradeNum = data['BuyTradeNum'].values[-4:]
        stk_weight = data['weight'].values[-4:]
        
        factor_raw = np.nansum(stk_BuyTradeNum / replace_zero(stk_BuyUniqueOrderNum) * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 4)
        return factor_mean[-1]
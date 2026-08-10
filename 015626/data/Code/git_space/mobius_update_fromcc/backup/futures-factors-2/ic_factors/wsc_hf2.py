import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero



class wsc_hf2(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['BuyTradeNum', 'weight', 'BuyUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        stk_BuyTradeNum = data['BuyTradeNum'].values[-25:]
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-25:]
        stk_weight = data['weight'].values[-25:]
        buow = replace_zero(np.nansum(stk_BuyUniqueOrderNum*stk_weight, axis=1))
        factor_init = np.nansum(stk_BuyTradeNum * stk_weight, axis=1) / buow
        factor_raw = ts_mean(factor_init, 25)
        return factor_raw[-1]
import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *
from help_functions_wsc import replace_zero


class wsc_hf1(FutureFactor):
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
        stk_BuyTradeNum = replace_zero(data['BuyTradeNum'].values[-25:])
        stk_BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-25:]
        stk_weight = data['weight'].values[-25:]
        factor_init = np.nansum(stk_BuyUniqueOrderNum * stk_weight / stk_BuyTradeNum, axis=1)
        factor_raw = -ts_mean(factor_init, 25)
        return factor_raw[-1]
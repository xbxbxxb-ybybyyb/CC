import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class sba_1_to_sa_w_ic(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_superorder_money_v2', 'SellTradeMoney', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_superorder_money_v2 = data['sell_superorder_money_v2'].values[-1]
        SellTradeMoney = data['SellTradeMoney'].values[-1]
        weight = data['weight'].values[-1]

        factor = np.nansum(sell_superorder_money_v2 / replace_zero(SellTradeMoney) * weight)
        return factor
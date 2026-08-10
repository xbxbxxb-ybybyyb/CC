import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class sa_to_sn_w_im(FutureFactor):

    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['SellTradeMoney', 'SellTradeNum', 'weight']
    normalize_size = 1
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        SellTradeMoney = data['SellTradeMoney'].values[-1]
        SellTradeNum = data['SellTradeNum'].values[-1]
        weight = data['weight'].values[-1]

        factor = np.nansum(SellTradeMoney / replace_zero(SellTradeNum) * weight)
        return factor
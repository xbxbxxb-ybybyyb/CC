import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_17_srch(FutureFactor):
    # ts_mean(sba_3_to_sa_w, 75) * sba_4_to_sa
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_midorder_money_v2', 'sell_smallorder_money_v2', 'SellTradeMoney', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        sell_midorder_money_v2 = data['sell_midorder_money_v2'].values[-75:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-75:]
        SellTradeMoney = data['SellTradeMoney'].values[-75:]
        weight = data['weight'].values[-75:]

        sba_3_to_sa_w = np.nansum(sell_midorder_money_v2 / replace_zero(SellTradeMoney) * weight, axis=1)
        sba_4_to_sa = np.nansum(sell_smallorder_money_v2, axis=1) / replace_zero(np.nansum(SellTradeMoney, axis=1))
        
        factor = ts_mean(sba_3_to_sa_w, 75) * sba_4_to_sa
        return factor[-1]
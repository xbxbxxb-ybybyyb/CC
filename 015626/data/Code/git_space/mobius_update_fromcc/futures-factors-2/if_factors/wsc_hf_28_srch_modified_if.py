import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_28_srch_modified_if(FutureFactor):
    # div2(mul2(coefficient_of_variation(sba_4_to_sa_w, 60), sba_4_to_sa), bba_4_r)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['sell_smallorder_money_v2', 'SellTradeMoney', 'weight', 'buy_smallorder_money']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_smallorder_money = data['buy_smallorder_money'].values[-60:]
        SellTradeMoney = data['SellTradeMoney'].values[-60:]
        weight = data['weight'].values[-60:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-60:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-60:]
        
        sba_4_to_sa_w = np.nansum(sell_smallorder_money_v2 / replace_zero(SellTradeMoney) * weight, axis=1)
        sba_4_to_sa = np.nansum(sell_smallorder_money_v2, axis=1) / replace_zero(np.nansum(SellTradeMoney, axis=1))
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1)
        
        factor = div2(mul2(coefficient_of_variation(sba_4_to_sa_w, 60), sba_4_to_sa), bba_4_r)
        return factor[-1]
import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_5_srch(FutureFactor):
    # sba_4_to_sa * cross_hub_num(bbn_4_to_bun_w, 100) * sba_4_to_sa * ba_to_bun_w
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_count', 'BuyUniqueOrderNum', 'weight', 'sell_smallorder_money_v2', 
                          'SellTradeMoney', 'BuyTradeMoney']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        BuyTradeMoney = data['BuyTradeMoney'].values[-205:]
        SellTradeMoney = data['SellTradeMoney'].values[-205:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-205:]
        buy_smallorder_count = data['buy_smallorder_count'].values[-205:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-205:]
        weight = data['weight'].values[-205:]
        
        sba_4_to_sa = np.nansum(sell_smallorder_money_v2, axis=1) / replace_zero(np.nansum(SellTradeMoney, axis=1))
        bbn_4_to_bun_w = np.nansum(buy_smallorder_count / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        ba_to_bun_w = np.nansum(BuyTradeMoney / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        
        factor = sba_4_to_sa * cross_hub_num(bbn_4_to_bun_w, 100) * sba_4_to_sa * ba_to_bun_w
        return factor[-1]
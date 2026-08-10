import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_15_srch(FutureFactor):
    # log(bbands_down(bbn_2_to_bun_w, 25) * sba_4_to_sa * ba_to_bun_w) + ts_corr(sba_4, sba_2_to_sa_w, 70)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyTradeMoney', 'SellTradeMoney', 'buy_bigorder_count', 'BuyUniqueOrderNum', 
                          'sell_bigorder_money_v2', 'sell_smallorder_money_v2', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_bigorder_count = data['buy_bigorder_count'].values[-70:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-70:]
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-70:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-70:]
        SellTradeMoney = data['SellTradeMoney'].values[-70:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-70:]        
        weight = data['weight'].values[-70:]
        
        bbn_2_to_bun_w = np.nansum(buy_bigorder_count / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        sba_4 = np.nansum(sell_smallorder_money_v2, axis=1)
        sba_4_to_sa = sba_4 / replace_zero(np.nansum(SellTradeMoney, axis=1))
        ba_to_bun_w = np.nansum(BuyTradeMoney / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        sba_2_to_sa_w = np.nansum(sell_bigorder_money_v2 / replace_zero(SellTradeMoney) * weight, axis=1)
        
        factor = log(bbands_down(bbn_2_to_bun_w, 25) * sba_4_to_sa * ba_to_bun_w) + ts_corr(sba_4, sba_2_to_sa_w, 70)
        return factor[-1]
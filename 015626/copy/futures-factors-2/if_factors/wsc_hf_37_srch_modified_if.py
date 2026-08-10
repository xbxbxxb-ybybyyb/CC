import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_37_srch_modified_if(FutureFactor):
    # sub2(sigmoid(ts_corr(ts_corr(bba_2_r_w, sbn_1_to_sun_w, 80), sbn_1_to_sun_w, 80)), midpoint(bun_r, 20))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_money', 'sell_bigorder_money_v2', 'weight', 'sell_superorder_count_v2',
                          'SellUniqueOrderNum', 'BuyUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_bigorder_money = data['buy_bigorder_money'].values[-160:]
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-160:]
        weight = data['weight'].values[-160:]
        sell_superorder_count_v2 = data['sell_superorder_count_v2'].values[-160:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-160:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-160:]
        
        bba_2_r_w = np.nansum(buy_bigorder_money / replace_zero(buy_bigorder_money + sell_bigorder_money_v2) * weight, axis=1)
        sbn_1_to_sun_w = np.nansum(sell_superorder_count_v2 / replace_zero(SellUniqueOrderNum) * weight, axis=1)
        bun_r = np.nansum(BuyUniqueOrderNum, axis=1) / replace_zero(np.nansum(BuyUniqueOrderNum + SellUniqueOrderNum, axis=1))
        
        factor = sub2(sigmoid(ts_corr(ts_corr(bba_2_r_w, sbn_1_to_sun_w, 80), sbn_1_to_sun_w, 80)), midpoint(bun_r, 20))
        return factor[-1]
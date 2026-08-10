import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_32_srch_modified_if(FutureFactor):
    # mul2(div2(dema(bba_1_to_ba_w, 40), bba_4_r_w), ts_std(sbn_3_to_sun_w, 40))
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_superorder_money', 'BuyTradeMoney', 'weight', 'buy_smallorder_money', 
                          'sell_smallorder_money_v2', 'sell_midorder_count_v2', 'SellUniqueOrderNum']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_superorder_money = data['buy_superorder_money'].values[-80:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-80:]
        weight = data['weight'].values[-80:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-80:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-80:]
        sell_midorder_count_v2 = data['sell_midorder_count_v2'].values[-80:]
        SellUniqueOrderNum = data['SellUniqueOrderNum'].values[-80:]
        
        bba_1_to_ba_w = np.nansum(buy_superorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bba_4_r_w = np.nansum(buy_smallorder_money / replace_zero(buy_smallorder_money + sell_smallorder_money_v2) *weight, axis=1)
        sbn_3_to_sun_w = np.nansum(sell_midorder_count_v2 / replace_zero(SellUniqueOrderNum) * weight, axis=1)
        
        factor = mul2(div2(dema(bba_1_to_ba_w, 40), bba_4_r_w), ts_std(sbn_3_to_sun_w, 40))
        return factor[-1]
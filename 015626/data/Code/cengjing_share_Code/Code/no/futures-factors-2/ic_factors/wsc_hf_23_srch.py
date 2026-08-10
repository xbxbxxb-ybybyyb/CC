import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_23_srch(FutureFactor):
    # (ts_skew(bbn_2_to_bun_w, 90) / bba_2_r_w + bba_4_to_ba) / ba_to_bun_w
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_bigorder_count', 'BuyUniqueOrderNum', 'buy_bigorder_money', 'sell_bigorder_money_v2',
                          'buy_smallorder_money', 'BuyTradeMoney', 'weight']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_bigorder_count = data['buy_bigorder_count'].values[-90:]
        BuyUniqueOrderNum = data['BuyUniqueOrderNum'].values[-90:]
        buy_bigorder_money = data['buy_bigorder_money'].values[-90:]
        sell_bigorder_money_v2 = data['sell_bigorder_money_v2'].values[-90:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-90:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-90:]
        weight = data['weight'].values[-90:]

        bbn_2_to_bun_w = np.nansum(buy_bigorder_count / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        bba_2_r_w = np.nansum(buy_bigorder_money / replace_zero(buy_bigorder_money + sell_bigorder_money_v2) * weight, axis=1)
        bba_4_to_ba = np.nansum(buy_smallorder_money, axis=1) / replace_zero(np.nansum(BuyTradeMoney, axis=1))
        ba_to_bun_w = np.nansum(BuyTradeMoney / replace_zero(BuyUniqueOrderNum) * weight, axis=1)
        
        factor = (ts_skew(bbn_2_to_bun_w, 90) / bba_2_r_w + bba_4_to_ba) / ba_to_bun_w
        return -factor[-1]
import numpy as np
from future_factor import FutureFactor
from help_functions_wsc import replace_zero
from operators_wsc_for_srch import *


    
class wsc_hf_29_srch_modified_if(FutureFactor):
    # -ts_distance_from_mean(midprice(bbands_up(bba_4_to_ba_w, 5), bba_4_r, 10), 75)
    data_type = 'IndexStock' 
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_smallorder_money', 'BuyTradeMoney', 'weight', 'sell_smallorder_money_v2']
    normalize_size = 1200
    normalize_type = 'ts_rank' 
    num_range = None
    handle_preadj = False
    
    def calculate(self, data):
        buy_smallorder_money = data['buy_smallorder_money'].values[-90:]
        BuyTradeMoney = data['BuyTradeMoney'].values[-90:]
        weight = data['weight'].values[-90:]
        buy_smallorder_money = data['buy_smallorder_money'].values[-90:]
        sell_smallorder_money_v2 = data['sell_smallorder_money_v2'].values[-90:]
        
        bba_4_to_ba_w = np.nansum(buy_smallorder_money / replace_zero(BuyTradeMoney) * weight, axis=1)
        bba_4_r = np.nansum(buy_smallorder_money, axis=1) / np.nansum(buy_smallorder_money + sell_smallorder_money_v2, axis=1)
        
        factor = -ts_distance_from_mean(midprice(bbands_up(bba_4_to_ba_w, 5), bba_4_r, 10), 75)
        return factor[-1]